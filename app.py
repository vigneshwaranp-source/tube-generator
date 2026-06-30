import streamlit as st
import cadquery as cq
import time
import math
import os
import json
import re
import google.generativeai as genai

st.set_page_config(layout="wide", page_title="Solid Tube Generator")
st.title("Lightning Fast Solid Tube Generator")
st.markdown("Generates a highly complex, 3D multi-body B-Rep solid model of a ribbed intake tube.")

# ==========================================
# UI: STATE MANAGEMENT
# ==========================================
if "tube_data" not in st.session_state:
    st.session_state.tube_data = [
        [440.615, -97.153, 241.057, 47.30],
        [434.009, -96.510, 238.835, 36.50],
        [388.715, -83.605, 223.622, 36.50],
        [358.672, -53.470, 213.579, 36.50],
        [350.239, -35.836, 212.048, 36.50],
        [288.364,  -3.164, 214.017, 36.50],
        [250.908,  -2.078, 208.424, 41.144]
    ]

# ==========================================
# 🤖 AI ASSISTANT (SIDEBAR)
# ==========================================
st.sidebar.title("🤖 CAD AI Assistant")
st.sidebar.markdown("Ask me to analyze parameters, or command me to change the tube!")

api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
elif "GEMINI_API_KEY" in os.environ:
    api_key = os.environ["GEMINI_API_KEY"]

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.sidebar.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.sidebar.chat_input("Ask about your CAD model..."):
        st.sidebar.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        context = f"""
        You are an expert Mechanical CAD AI Assistant helping a user design a ribbed intake tube.
        The current active data (7 points, format: [X, Y, Z, Diameter]) is:
        {st.session_state.tube_data}
        
        RULES:
        1. If the user asks a general question, just reply normally.
        2. If the user asks you to modify the tube, YOU MUST output the full updated list of all 7 points inside a JSON code block like this:
        ```json
        [
          [x1, y1, z1, dia1],
          [x2, y2, z2, dia2],
          [x3, y3, z3, dia3],
          [x4, y4, z4, dia4],
          [x5, y5, z5, dia5],
          [x6, y6, z6, dia6],
          [x7, y7, z7, dia7]
        ]
        ```
        Always include the JSON block if a change is requested, followed by a brief explanation.
        
        User prompt: {prompt}
        """
        
        with st.sidebar.spinner("Thinking..."):
            try:
                response = model.generate_content(context)
                ai_reply = response.text
                
                json_match = re.search(r'```json\n(.*?)\n```', ai_reply, re.DOTALL)
                
                if json_match:
                    try:
                        new_data = json.loads(json_match.group(1))
                        if len(new_data) == 7:
                            st.session_state.tube_data = new_data
                            update_msg = "✅ **I have updated the parameters on your screen!** Please review the numbers and click the **Generate Intake Tube Model** button to render your changes."
                            st.session_state.messages.append({"role": "assistant", "content": update_msg})
                            st.rerun() 
                    except Exception as e:
                        st.sidebar.error("Failed to apply AI changes.")
                
                clean_reply = re.sub(r'```json\n(.*?)\n```', '', ai_reply, flags=re.DOTALL).strip()
                if clean_reply:
                    st.sidebar.chat_message("assistant").markdown(clean_reply)
                    st.session_state.messages.append({"role": "assistant", "content": clean_reply})
                    
            except Exception as e:
                st.sidebar.error(f"AI Connection Error: {e}")
else:
    st.sidebar.warning("⚠️ **API Key Missing**\n\nTo activate the AI, go to your Streamlit Cloud App Settings > Secrets, and add:\n`GEMINI_API_KEY = \"your_actual_key_here\"`")


# ==========================================
# UI: USER INPUTS FOR POINTS AND DIAMETERS
# ==========================================
st.subheader("Trajectory Coordinates & Diameters")
user_data = []

cols = st.columns([1, 2, 2, 2, 2])
cols[0].markdown("**Point**")
cols[1].markdown("**X**")
cols[2].markdown("**Y**")
cols[3].markdown("**Z**")
cols[4].markdown("**Outer Dia (mm)**")

for i in range(7):
    dx, dy, dz, ddia = st.session_state.tube_data[i]
    cols = st.columns([1, 2, 2, 2, 2])
    cols[0].markdown(f"**P{i+1}**")
    
    x = cols[1].number_input(f"X{i+1}", value=float(dx), format="%.3f", key=f"x{i}", label_visibility="collapsed")
    y = cols[2].number_input(f"Y{i+1}", value=float(dy), format="%.3f", key=f"y{i}", label_visibility="collapsed")
    z = cols[3].number_input(f"Z{i+1}", value=float(dz), format="%.3f", key=f"z{i}", label_visibility="collapsed")
    dia = cols[4].number_input(f"Dia{i+1}", value=float(ddia), format="%.3f", key=f"d{i}", label_visibility="collapsed")
    
    st.session_state.tube_data[i] = [x, y, z, dia]
    user_data.append(((x, y, z), dia / 2.0))

st.markdown("---")

# ==========================================
# CAD GENERATION LOGIC 
# ==========================================
if st.button("Generate Intake Tube Model"):
    status_text = st.empty()
    
    with st.spinner("Compiling CAD geometry and generating web renders... Please wait."):
        try:
            status_text.info("--- LIGHTNING FAST SOLID TUBE GENERATOR (FINAL) ---")
            start_time = time.time()
            
            data = user_data
            pts = [d[0] for d in data]
            radii = [d[1] for d in data]
            
            wall_thickness = 3.5
            rib_h = 2.5
            rib_w = 2.5
            rib_fillet = 1.24
            
            status_text.info("Mapping 3D spline trajectory...")
            path = cq.Workplane("XY").spline(pts)
            wire = path.wire().val()
            exact_length = wire.Length()
            chord_lengths = [0.0]
            
            for i in range(1, len(pts)):
                d = (cq.Vector(pts[i]) - cq.Vector(pts[i-1])).Length
                chord_lengths.append(chord_lengths[-1] + d)
                
            total_chord = chord_lengths[-1]
            t_control = [c / total_chord for c in chord_lengths]
            
            status_text.info("Running automated curvature and pinch checks...")
            is_smooth = True
            suggested_pts = list(pts)
            
            for i in range(1, len(pts)-1):
                p0 = cq.Vector(pts[i-1])
                p1 = cq.Vector(pts[i])
                p2 = cq.Vector(pts[i+1])
                v1 = p1 - p0
                v2 = p2 - p1

                try:
                    angle = v1.getAngle(v2) * (180.0 / math.pi)
                except:
                    angle = 0.0
                    
                dist = v1.Length + v2.Length
                local_dia = radii[i] * 2
                
                if angle > 45 and dist < local_dia * 3:
                    is_smooth = False
                    st.warning(f"⚠ ️ WARNING: Geometry Pinch Detected at Point {i+1} {pts[i]}!\n-> The {round(angle, 1)}° bend is too sharp for a {local_dia}mm diameter tube.")

                midpoint = (p0 + p2) * 0.5
                suggested_p = p1 + (midpoint - p1) * 0.4
                suggested_pts[i] = (round(suggested_p.x, 3), round(suggested_p.y, 3), round(suggested_p.z, 3))
                
            if not is_smooth:
                st.error("❌  GENERATION HALTED: To prevent a corrupt model, please update your coordinates with these optimized points:")
                for idx, sp in enumerate(suggested_pts):
                    st.write(f"Point {idx+1}: {sp}")
                raise ValueError("Sharp geometry detected. Please apply the suggested coordinates above and re-run.")
                
            status_text.info("✅  Geometry check passed! Profile is smooth.")
            
            def get_smooth_radius(t):
                for i in range(len(t_control)-1):
                    if t_control[i] <= t <= t_control[i+1]:
                        t0, t1 = t_control[i], t_control[i+1]
                        r0, r1 = radii[i], radii[i+1]
                        if t1 == t0: return r0
                        f = (t - t0) / (t1 - t0)
                        f_smooth = f * f * (3 - 2 * f)
                        return r0 + (r1 - r0) * f_smooth
                return radii[-1]
                
            status_text.info("Evaluating 60 filleted slices (This takes ~5 seconds)...")
            outer_wires = []
            inner_wires = []
            global_up = cq.Vector(0, 0, 1)
            num_slices = 60
            
            for i in range(num_slices):
                t = i / (num_slices - 1)
                pos = wire.positionAt(t)
                tangent = wire.tangentAt(t)

                x_dir = tangent.cross(global_up)
                if x_dir.Length < 0.001: x_dir = tangent.cross(cq.Vector(0, 1, 0))
                plane = cq.Plane(origin=pos, xDir=x_dir, normal=tangent)
                R = get_smooth_radius(t)

                sketch = (cq.Sketch()
                    .circle(R)
                    .rect(R*2 + (rib_h*2), rib_w)
                    .rect(rib_w, R*2 + (rib_h*2))
                    .clean()
                    .vertices()
                    .fillet(rib_fillet))

                outer_wire_2d = sketch._faces.Faces()[0].outerWire()
                outer_wires.append(outer_wire_2d.moved(cq.Location(plane)))

                inner_r = R - wall_thickness
                inner_wires.append(cq.Workplane(plane).circle(inner_r).wire().val())
                
            solid_outer = cq.Solid.makeLoft(outer_wires, ruled=False)
            solid_inner = cq.Solid.makeLoft(inner_wires, ruled=False)
            
            status_text.info("Generating fully filleted transverse rings...")
            rib_spacing = 30.0
            num_rings = int(exact_length / rib_spacing)
            ring_list = []
            
            for i in range(1, num_rings + 1):
                d = i * rib_spacing
                if d >= exact_length: break

                t = d / exact_length
                pos = wire.positionAt(t)
                tangent = wire.tangentAt(t)
                R = get_smooth_radius(t)

                x_dir_radial = tangent.cross(global_up)
                if x_dir_radial.Length < 0.001:
                    x_dir_radial = tangent.cross(cq.Vector(0, 1, 0))

                normal_rev = tangent.cross(x_dir_radial)
                plane_rev = cq.Plane(origin=pos, xDir=tangent, normal=normal_rev)

                ring_prof = (cq.Workplane(plane_rev)
                    .moveTo(-0.75, R + 2.6)
                    .lineTo( 0.75, R + 2.6)
                    .threePointArc((1.1035, R + 2.4535), (1.25, R + 2.1)) 
                    .lineTo( 1.25, R + 1.5)
                    .threePointArc((1.5429, R + 0.7929), (2.25, R + 0.5)) 
                    .lineTo( 2.25, R - 0.5)
                    .lineTo(-2.25, R - 0.5)
                    .lineTo(-2.25, R + 0.5)
                    .threePointArc((-1.5429, R + 0.7929), (-1.25, R + 1.5)) 
                    .lineTo(-1.25, R + 2.1)
                    .threePointArc((-1.1035, R + 2.4535), (-0.75, R + 2.6)) 
                    .close()
                )

                ring = ring_prof.revolve(360, (0,0,0), (1,0,0)).val()
                ring_list.append(ring)
                
            status_text.info("Generating Throttle Body Flange at P7...")
            p7_pos = wire.positionAt(1.0)
            p7_tangent = wire.tangentAt(1.0)
            x_dir_p7 = p7_tangent.cross(global_up)
            
            if x_dir_p7.Length < 0.001: x_dir_p7 = p7_tangent.cross(cq.Vector(0, 1, 0))
            plane_p7 = cq.Plane(origin=p7_pos, xDir=x_dir_p7, normal=p7_tangent)
            
            p7_dia = radii[-1] * 2.0
            cyl_inner_dia = p7_dia + 2.5
            cyl_inner_r = cyl_inner_dia / 2.0
            cyl_outer_r = cyl_inner_r + 3.5
            cyl_length = 12.0
            
            plane_fillet_start = cq.Plane(origin=p7_pos + (p7_tangent * -2.0), xDir=x_dir_p7, normal=p7_tangent)
            flange_fillet = (cq.Workplane(plane_fillet_start)
                .circle((p7_dia / 2.0) - 0.1)
                .workplane(offset=2.0)
                .circle(cyl_outer_r)
                .loft(combine=False)
                .val())
                
            plane_cyl_start = cq.Plane(origin=p7_pos + (p7_tangent * -0.5), xDir=x_dir_p7, normal=p7_tangent)
            throttle_cyl = (cq.Workplane(plane_cyl_start)
                .circle(cyl_outer_r)
                .circle(cyl_inner_r)
                .extrude(cyl_length + 0.5)
                .val())
                
            t_rib_rad = 0.5
            p7_end_pos = p7_pos + (p7_tangent * cyl_length)
            throttle_rib_1 = cq.Solid.makeTorus(cyl_outer_r, t_rib_rad, p7_pos, p7_tangent)
            throttle_rib_2 = cq.Solid.makeTorus(cyl_outer_r, t_rib_rad, p7_end_pos, p7_tangent)
            
            status_text.info("Generating Dual-Flange Mounting Feature at P3...")
            p3_idx = 2
            p3_t = t_control[p3_idx]
            p3_pos = wire.positionAt(p3_t)
            p3_tangent = wire.tangentAt(p3_t)
            x_dir_p3 = p3_tangent.cross(global_up)
            
            if x_dir_p3.Length < 0.001: x_dir_p3 = p3_tangent.cross(cq.Vector(0, 1, 0))
            plane_p3 = cq.Plane(origin=p3_pos, xDir=x_dir_p3, normal=p3_tangent)
            p3_rad = radii[p3_idx]
            p3_dia = p3_rad * 2.0
            
            c1_r = (p3_dia + 7.0) / 2.0   
            c2_r = (p3_dia + 15.0) / 2.0  
            mount_thick = 3.5
            mount_gap = 3.0
            
            mount_c1 = (cq.Workplane(plane_p3)
                .circle(c1_r).circle(p3_rad - 1.0)
                .extrude(mount_thick).val())
                
            plane_c1_fillet = cq.Plane(origin=p3_pos + (p3_tangent * -2.0), xDir=x_dir_p3, normal=p3_tangent)
            mount_c1_fillet = (cq.Workplane(plane_c1_fillet)
                .circle(p3_rad - 1.0)
                .workplane(offset=2.0)
                .circle(c1_r)
                .loft(combine=False).val())
                
            plane_gap = cq.Plane(origin=p3_pos + (p3_tangent * mount_thick), xDir=x_dir_p3, normal=p3_tangent)
            gap_rib_remover = (cq.Workplane(plane_gap)
                .circle(p3_rad + rib_h + 5.0) 
                .circle(p3_rad)               
                .extrude(mount_gap).val())
                
            c2_offset = mount_thick + mount_gap
            plane_c2 = cq.Plane(origin=p3_pos + (p3_tangent * c2_offset), xDir=x_dir_p3, normal=p3_tangent)
            mount_c2 = (cq.Workplane(plane_c2)
                .circle(c2_r).circle(p3_rad - 1.0)
                .extrude(mount_thick).val())
                
            plane_c2_fillet = cq.Plane(origin=p3_pos + (p3_tangent * (c2_offset + mount_thick)), xDir=x_dir_p3, normal=p3_tangent)
            mount_c2_fillet = (cq.Workplane(plane_c2_fillet)
                .circle(c2_r)
                .workplane(offset=2.0)
                .circle(p3_rad - 1.0)
                .loft(combine=False).val())
                
            # ==========================================
            # 8. BOOLEAN FUSION (Exactly from your Golden Code)
            # ==========================================
            status_text.info("Fusing all bodies into a single water-tight Solid (Please wait ~12s)...")
            all_rings = cq.Compound.makeCompound(ring_list)
            
            main_body = cq.Workplane().add(solid_outer)
            main_body = main_body.cut(cq.Workplane().add(gap_rib_remover))
            
            main_body = (main_body
                .union(cq.Workplane().add(all_rings))
                .union(cq.Workplane().add(flange_fillet))
                .union(cq.Workplane().add(throttle_cyl))
                .union(cq.Workplane().add(throttle_rib_1))
                .union(cq.Workplane().add(throttle_rib_2))
                .union(cq.Workplane().add(mount_c1))
                .union(cq.Workplane().add(mount_c1_fillet))
                .union(cq.Workplane().add(mount_c2))
                .union(cq.Workplane().add(mount_c2_fillet)))
                
            final_solid_tube = main_body.cut(cq.Workplane().add(solid_inner))
            
            # ==========================================
            # 9. RENDER 2D SVG PROJECTIONS ON WEBPAGE
            # ==========================================
            status_text.info("Rendering 2D engineering views for the web page... (Takes a few seconds)")
            
            view_angles = {
                "Isometric": (1, -1, 1),
                "Front": (0, -1, 0),
                "Top": (0, 0, 1),
                "Bottom": (0, 0, -1),
                "Side": (1, 0, 0)
            }
            
            svg_contents = {}
            for view_name, proj_dir in view_angles.items():
                svg_path = os.path.join(os.getcwd(), f"{view_name}.svg")
                opt = {
                    "width": 800,
                    "height": 600,
                    "marginLeft": 10,
                    "marginTop": 10,
                    "showAxes": False,
                    "projectionDir": proj_dir,
                    "strokeWidth": 0.8,
                    "strokeColor": (0, 0, 0),
                    "showHidden": False
                }
                
                # Export the underlying shape to ensure SVG catches everything cleanly
                cq.exporters.export(final_solid_tube.val(), svg_path, exportType='SVG', opt=opt)
                
                with open(svg_path, "r") as f:
                    svg_contents[view_name] = f.read()
                os.remove(svg_path) 

            # ==========================================
            # 10. EXPORT ASSEMBLY & RENDER UI
            # ==========================================
            status_text.info("Packaging Solid Body and Wireframes into STEP format...")
            assy = cq.Assembly()
            assy.add(final_solid_tube, name="Final_Solid_Tube", color=cq.Color("orange"))
            assy.add(path, name="Ref_Center_Curve", color=cq.Color("blue"))
            
            for i in range(len(pts)):
                p_coord = pts[i]
                r = radii[i]
                t = t_control[i]
                tangent = wire.tangentAt(t)
                x_dir = tangent.cross(global_up)
                if x_dir.Length < 0.001: x_dir = tangent.cross(cq.Vector(0, 1, 0))
                plane = cq.Plane(origin=cq.Vector(p_coord), xDir=x_dir, normal=tangent)
                pt_vertex = cq.Vertex.makeVertex(*p_coord)
                assy.add(pt_vertex, name=f"Ref_Point_{i+1}", color=cq.Color("black"))
                ref_circle = cq.Workplane(plane).circle(r).wire().val()
                assy.add(ref_circle, name=f"Ref_Circle_{i+1}", color=cq.Color("green"))
                
            filename = "Final_Intake_Tube_Model.stp"
            filepath = os.path.join(os.getcwd(), filename)
            assy.save(filepath, exportType='STEP')
            
            end_time = time.time()
            status_text.empty() 
            st.success(f"✅ SUCCESS! Solid Part and Web Renders generated in {round(end_time - start_time, 1)} seconds.")
            
            st.markdown("### Interactive Engineering Views")
            tabs = st.tabs(list(view_angles.keys()))
            
            for idx, view_name in enumerate(view_angles.keys()):
                with tabs[idx]:
                    html_wrapper = f"""
                    <div style="text-align: center; background-color: #ffffff; border: 2px solid #e6e6e6; padding: 15px; border-radius: 8px;">
                        {svg_contents[view_name]}
                    </div>
                    """
                    st.markdown(html_wrapper, unsafe_allow_html=True)
            
            st.markdown("---")
            
            with open(filepath, "rb") as file:
                st.download_button(
                    label="⬇️ Download 3D STEP File",
                    data=file,
                    file_name=filename,
                    mime="application/octet-stream",
                    use_container_width=True
                )

        except ValueError as ve:
            status_text.empty()
            st.error(str(ve))
        except Exception as e:
            status_text.empty()
            st.error(f"An unexpected error occurred during geometric modeling:\n{e}")
