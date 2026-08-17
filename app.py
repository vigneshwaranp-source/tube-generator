import streamlit as st

st.set_page_config(page_title="CATIA Segmented Tube (Main Profile Only)", page_icon="🧩", layout="wide")

st.title("🧩 CATIA V5: Segmented Loft & Fillet (Main Tube Only)")
st.write("This macro builds ONLY the main variable tube wireframe and surfaces. All points, planes, and circles will be neatly named using your Point IDs.")

# --- 1. USER INTERFACE ---
st.header("1. Global Tube Parameters")
transition_fillet = st.number_input("Segment Blend Fillet (mm)", value=40.0, step=5.0)

st.header("2. Coordinates, Segment Radii & IDs (7 Points)")
points = []
for i in range(1, 8):
    cols = st.columns([1.5, 1, 1, 1, 1]) 
    default_x = [0.0, 0.0, 150.0, 300.0, 300.0, 150.0, 0.0]
    default_y = [0.0, 0.0, 0.0, 150.0, 300.0, 450.0, 450.0]
    default_z = [0.0, 200.0, 300.0, 300.0, 450.0, 600.0, 800.0]
    default_r = [30.0, 35.0, 40.0, 45.0, 40.0, 35.0, 30.0]
    
    with cols[0]:
        pt_id = st.text_input(f"P{i} ID", value=f"Point_{i}", key=f"id{i}")
    with cols[1]:
        x = st.number_input(f"P{i} X", value=default_x[i-1], key=f"x{i}")
    with cols[2]:
        y = st.number_input(f"P{i} Y", value=default_y[i-1], key=f"y{i}")
    with cols[3]:
        z = st.number_input(f"P{i} Z", value=default_z[i-1], key=f"z{i}")
    with cols[4]:
        r = st.number_input(f"Segment Radius", value=default_r[i-1], key=f"r{i}")
    
    points.append((pt_id, x, y, z, r))

# --- 2. VBSCRIPT GENERATION LOGIC ---
vbscript_code = f"""Sub CATMain()
    Dim partDocument1
    Set partDocument1 = CATIA.ActiveDocument
    Dim part1
    Set part1 = partDocument1.Part
    Dim hsf
    Set hsf = part1.HybridShapeFactory
    Dim hybridBodies1
    Set hybridBodies1 = part1.HybridBodies
    
    Dim geomSet
    Set geomSet = hybridBodies1.Add()
    geomSet.Name = "Macro_Tube_Geometry"

    ' ==========================================
    ' 1. CREATE POINTS & SPLINE
    ' ==========================================
"""

for i, (p_id, px, py, pz, pr) in enumerate(points, start=1):
    vbscript_code += f"""    Dim pt{i} : Set pt{i} = hsf.AddNewPointCoord({px}, {py}, {pz}) : pt{i}.Name = "{p_id}" : geomSet.AppendHybridShape pt{i}
    Dim refPt{i} : Set refPt{i} = part1.CreateReferenceFromObject(pt{i})
"""

vbscript_code += f"""
    Dim spline : Set spline = hsf.AddNewSpline() : spline.SetSplineType 0 : spline.SetClosing 0
"""
for i in range(1, 8):
    vbscript_code += f"    spline.AddPoint refPt{i}\n"

vbscript_code += f"""    geomSet.AppendHybridShape spline
    Dim refSpline : Set refSpline = part1.CreateReferenceFromObject(spline)

    ' ==========================================
    ' 2. CREATE NAMED PLANES & CIRCLES ON SPLINE
    ' ==========================================
"""

for i, (p_id, px, py, pz, pr) in enumerate(points, start=1):
    vbscript_code += f"""    ' --- Section {i}: {p_id} ---
    Dim plane{i} : Set plane{i} = hsf.AddNewPlaneNormal(refSpline, refPt{i}) : plane{i}.Name = "{p_id}_Plane" : geomSet.AppendHybridShape plane{i}
    Dim refPlane{i} : Set refPlane{i} = part1.CreateReferenceFromObject(plane{i})

    Dim circle{i} : Set circle{i} = hsf.AddNewCircleCtrRad(refPt{i}, refPlane{i}, False, {pr}) : circle{i}.Name = "{p_id}_Profile" : geomSet.AppendHybridShape circle{i}
    Dim refCircle{i} : Set refCircle{i} = part1.CreateReferenceFromObject(circle{i})

    ' Closing point for Loft (0 distance on curve)
    Dim pt_c1_{i} : Set pt_c1_{i} = hsf.AddNewPointOnCurveFromDistance(refCircle{i}, 0.0, False) : pt_c1_{i}.Name = "{p_id}_ClosePt" : geomSet.AppendHybridShape pt_c1_{i}
    Dim ref_pt_c1_{i} : Set ref_pt_c1_{i} = part1.CreateReferenceFromObject(pt_c1_{i})
"""

vbscript_code += f"""
    ' ==========================================
    ' 3. CREATE INDIVIDUAL SEGMENT LOFTS
    ' ==========================================
"""
for i in range(1, 7):
    p1_id = points[i-1][0]
    p2_id = points[i][0]
    vbscript_code += f"""    Dim loft{i} : Set loft{i} = hsf.AddNewLoft() : loft{i}.SectionCoupling = 1
    loft{i}.AddSectionToLoft refCircle{i}, 1, ref_pt_c1_{i}
    loft{i}.AddSectionToLoft refCircle{i+1}, 1, ref_pt_c1_{i+1}
    loft{i}.Name = "Loft_{p1_id}_to_{p2_id}"
    geomSet.AppendHybridShape loft{i}
    Dim refLoft{i} : Set refLoft{i} = part1.CreateReferenceFromObject(loft{i})
"""

vbscript_code += f"""
    part1.Update()

    ' ==========================================
    ' 4. CASCADING SURFACE FILLETS (SMOOTHING)
    ' ==========================================
"""
vbscript_code += f"""    Dim fillet1 : Set fillet1 = hsf.AddNewFilletBiTangent(refLoft1, refLoft2, {transition_fillet}, 1, 1, 1, 1) : fillet1.Name = "Blend_1" : geomSet.AppendHybridShape fillet1 : Dim refFillet1 : Set refFillet1 = part1.CreateReferenceFromObject(fillet1)
    Dim fillet2 : Set fillet2 = hsf.AddNewFilletBiTangent(refFillet1, refLoft3, {transition_fillet}, 1, 1, 1, 1) : fillet2.Name = "Blend_2" : geomSet.AppendHybridShape fillet2 : Dim refFillet2 : Set refFillet2 = part1.CreateReferenceFromObject(fillet2)
    Dim fillet3 : Set fillet3 = hsf.AddNewFilletBiTangent(refFillet2, refLoft4, {transition_fillet}, 1, 1, 1, 1) : fillet3.Name = "Blend_3" : geomSet.AppendHybridShape fillet3 : Dim refFillet3 : Set refFillet3 = part1.CreateReferenceFromObject(fillet3)
    Dim fillet4 : Set fillet4 = hsf.AddNewFilletBiTangent(refFillet3, refLoft5, {transition_fillet}, 1, 1, 1, 1) : fillet4.Name = "Blend_4" : geomSet.AppendHybridShape fillet4 : Dim refFillet4 : Set refFillet4 = part1.CreateReferenceFromObject(fillet4)
    Dim fillet5 : Set fillet5 = hsf.AddNewFilletBiTangent(refFillet4, refLoft6, {transition_fillet}, 1, 1, 1, 1) : fillet5.Name = "Main_Tube_Final_Surface" : geomSet.AppendHybridShape fillet5 : Dim finalSurfaceRef : Set finalSurfaceRef = part1.CreateReferenceFromObject(fillet5)
    
    part1.Update()
End Sub
"""

# --- 3. DOWNLOAD BUTTON ---
st.header("3. Generate & Download")
st.download_button(
    label="⬇️ Download CATIA Macro (.catvbs)",
    data=vbscript_code,
    file_name="MakeCoreTubeProfile.catvbs",
    mime="text/plain"
)
