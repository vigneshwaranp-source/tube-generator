import streamlit as st

st.set_page_config(page_title="CATIA Segmented Tube Generator", page_icon="🧩", layout="wide")

st.title("🧩 CATIA V5: Segmented Tube & Fillet Generator")
st.write("This macro builds a highly stable variable tube by creating individual sweeps for each segment and blending them automatically using Surface Fillets.")

# --- 1. USER INTERFACE ---
st.header("1. Global Tube Parameters")
col1, col2, col3 = st.columns(3)
with col1:
    main_thickness = st.number_input("Main Tube Thickness (mm)", value=2.5, step=0.5)
    transition_fillet = st.number_input("Segment Blend Fillet (mm)", value=30.0, step=5.0)
with col2:
    vert_rib_radius = st.number_input("Vertical Wire Radius (mm)", value=1.0, step=0.5)
with col3:
    circ_rib_radius = st.number_input("Circular Rib Radius (mm)", value=1.5, step=0.5)
    circ_rib_spacing = st.number_input("Circular Rib Spacing (mm)", value=20.0, step=5.0)

st.header("2. Coordinates & Segment Radii (7 Points)")
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

    Dim ribsSet
    Set ribsSet = hybridBodies1.Add()
    ribsSet.Name = "Circular_Ribs"

    ' ==========================================
    ' 1. CREATE POINTS
    ' ==========================================
"""

for i, (p_id, px, py, pz, pr) in enumerate(points, start=1):
    vbscript_code += f"""    Dim pt{i}
    Set pt{i} = hsf.AddNewPointCoord({px}, {py}, {pz})
    pt{i}.Name = "{p_id}"
    geomSet.AppendHybridShape pt{i}
    Dim refPt{i} : Set refPt{i} = part1.CreateReferenceFromObject(pt{i})
"""

vbscript_code += f"""
    ' ==========================================
    ' 2. MAIN SPLINE (For Rib Guides Only)
    ' ==========================================
    Dim spline
    Set spline = hsf.AddNewSpline()
    spline.SetSplineType 0
    spline.SetClosing 0
"""
for i in range(1, 8):
    vbscript_code += f"    spline.AddPoint refPt{i}\n"

vbscript_code += f"""    geomSet.AppendHybridShape spline
    Dim refSpline : Set refSpline = part1.CreateReferenceFromObject(spline)

    ' ==========================================
    ' 3. CREATE INDIVIDUAL SEGMENTS & SWEEPS
    ' ==========================================
"""

# Generate Lines and Sweeps for each of the 6 segments
for i in range(1, 7):
    r_val = points[i-1][4] # Using the radius defined at the start of the segment
    vbscript_code += f"""    ' Segment {i}
    Dim line{i}
    Set line{i} = hsf.AddNewLinePtPt(refPt{i}, refPt{i+1})
    geomSet.AppendHybridShape line{i}
    Dim refLine{i} : Set refLine{i} = part1.CreateReferenceFromObject(line{i})

    Dim sweep{i}
    Set sweep{i} = hsf.AddNewSweepCircle(refLine{i})
    sweep{i}.Mode = 6
    sweep{i}.SetRadius 1, {r_val}
    sweep{i}.Name = "Segment_Sweep_{i}"
    geomSet.AppendHybridShape sweep{i}
    Dim refSweep{i} : Set refSweep{i} = part1.CreateReferenceFromObject(sweep{i})
"""

vbscript_code += f"""
    part1.Update()

    ' ==========================================
    ' 4. CASCADING SURFACE FILLETS (BLENDING)
    ' ==========================================
    ' We use Bi-Tangent fillets with Trim=1 to automatically join the segments
"""

# Cascade the fillets: Fillet1 blends Sweep1&2. Fillet2 blends Fillet1&Sweep3.
vbscript_code += f"""    Dim fillet1
    ' Arguments: Surface1, Surface2, Radius, Orient1, Orient2, Trim1, Trim2
    Set fillet1 = hsf.AddNewFilletBiTangent(refSweep1, refSweep2, {transition_fillet}, 1, 1, 1, 1)
    geomSet.AppendHybridShape fillet1
    Dim refFillet1 : Set refFillet1 = part1.CreateReferenceFromObject(fillet1)

    Dim fillet2
    Set fillet2 = hsf.AddNewFilletBiTangent(refFillet1, refSweep3, {transition_fillet}, 1, 1, 1, 1)
    geomSet.AppendHybridShape fillet2
    Dim refFillet2 : Set refFillet2 = part1.CreateReferenceFromObject(fillet2)

    Dim fillet3
    Set fillet3 = hsf.AddNewFilletBiTangent(refFillet2, refSweep4, {transition_fillet}, 1, 1, 1, 1)
    geomSet.AppendHybridShape fillet3
    Dim refFillet3 : Set refFillet3 = part1.CreateReferenceFromObject(fillet3)

    Dim fillet4
    Set fillet4 = hsf.AddNewFilletBiTangent(refFillet3, refSweep5, {transition_fillet}, 1, 1, 1, 1)
    geomSet.AppendHybridShape fillet4
    Dim refFillet4 : Set refFillet4 = part1.CreateReferenceFromObject(fillet4)

    Dim fillet5
    Set fillet5 = hsf.AddNewFilletBiTangent(refFillet4, refSweep6, {transition_fillet}, 1, 1, 1, 1)
    fillet5.Name = "Main_Tube_Surface"
    geomSet.AppendHybridShape fillet5
    Dim finalSurfaceRef : Set finalSurfaceRef = part1.CreateReferenceFromObject(fillet5)

    part1.Update()

    ' ==========================================
    ' 5. VERTICAL & CIRCULAR RIBS (Along Spline)
    ' ==========================================
    ' We project 4 direction lines from Point 1, sweep them as ribbons, and intersect the final surface
    Dim dirR, dirL, dirU, dirD
    Set dirR = hsf.AddNewDirectionByCoord(1, 0, 0)
    Set dirL = hsf.AddNewDirectionByCoord(-1, 0, 0)
    Set dirU = hsf.AddNewDirectionByCoord(0, 1, 0)
    Set dirD = hsf.AddNewDirectionByCoord(0, -1, 0)

    Dim lineR : Set lineR = hsf.AddNewLinePtDir(refPt1, dirR, 0.0, 150.0, False) : geomSet.AppendHybridShape lineR
    Dim ribbonR : Set ribbonR = hsf.AddNewSweepExplicit(part1.CreateReferenceFromObject(lineR), refSpline) : geomSet.AppendHybridShape ribbonR
    Dim curveR : Set curveR = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonR), finalSurfaceRef) : geomSet.AppendHybridShape curveR
    Dim vRibR : Set vRibR = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(curveR)) : vRibR.Mode = 6 : vRibR.SetRadius 1, {vert_rib_radius} : geomSet.AppendHybridShape vRibR

    Dim lineL : Set lineL = hsf.AddNewLinePtDir(refPt1, dirL, 0.0, 150.0, False) : geomSet.AppendHybridShape lineL
    Dim ribbonL : Set ribbonL = hsf.AddNewSweepExplicit(part1.CreateReferenceFromObject(lineL), refSpline) : geomSet.AppendHybridShape ribbonL
    Dim curveL : Set curveL = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonL), finalSurfaceRef) : geomSet.AppendHybridShape curveL
    Dim vRibL : Set vRibL = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(curveL)) : vRibL.Mode = 6 : vRibL.SetRadius 1, {vert_rib_radius} : geomSet.AppendHybridShape vRibL

    Dim lineU : Set lineU = hsf.AddNewLinePtDir(refPt1, dirU, 0.0, 150.0, False) : geomSet.AppendHybridShape lineU
    Dim ribbonU : Set ribbonU = hsf.AddNewSweepExplicit(part1.CreateReferenceFromObject(lineU), refSpline) : geomSet.AppendHybridShape ribbonU
    Dim curveU : Set curveU = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonU), finalSurfaceRef) : geomSet.AppendHybridShape curveU
    Dim vRibU : Set vRibU = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(curveU)) : vRibU.Mode = 6 : vRibU.SetRadius 1, {vert_rib_radius} : geomSet.AppendHybridShape vRibU

    Dim lineD : Set lineD = hsf.AddNewLinePtDir(refPt1, dirD, 0.0, 150.0, False) : geomSet.AppendHybridShape lineD
    Dim ribbonD : Set ribbonD = hsf.AddNewSweepExplicit(part1.CreateReferenceFromObject(lineD), refSpline) : geomSet.AppendHybridShape ribbonD
    Dim curveD : Set curveD = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonD), finalSurfaceRef) : geomSet.AppendHybridShape curveD
    Dim vRibD : Set vRibD = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(curveD)) : vRibD.Mode = 6 : vRibD.SetRadius 1, {vert_rib_radius} : geomSet.AppendHybridShape vRibD

    ' Circular Ribs
    Dim TheSPAWorkbench : Set TheSPAWorkbench = partDocument1.GetWorkbench("SPAWorkbench")
    Dim measurableSpline : Set measurableSpline = TheSPAWorkbench.GetMeasurable(refSpline)
    Dim totalLength : totalLength = measurableSpline.Length
    Dim currentDist : currentDist = {circ_rib_spacing}
    Dim ribCounter : ribCounter = 1

    Do While currentDist < (totalLength - 1.0)
        Dim ptOnCurve : Set ptOnCurve = hsf.AddNewPointOnCurveFromDistance(refSpline, currentDist, True) : ribsSet.AppendHybridShape ptOnCurve
        Dim planeNormal : Set planeNormal = hsf.AddNewPlaneNormal(refSpline, part1.CreateReferenceFromObject(ptOnCurve)) : ribsSet.AppendHybridShape planeNormal
        Dim circleIntersect : Set circleIntersect = hsf.AddNewIntersection(part1.CreateReferenceFromObject(planeNormal), finalSurfaceRef) : circleIntersect.Name = "Rib_Circle_" & CStr(ribCounter) : ribsSet.AppendHybridShape circleIntersect
        Dim ribSweep : Set ribSweep = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(circleIntersect)) : ribSweep.Mode = 6 : ribSweep.SetRadius 1, {circ_rib_radius} : ribsSet.AppendHybridShape ribSweep
        currentDist = currentDist + {circ_rib_spacing}
        ribCounter = ribCounter + 1
    Loop
    
    part1.Update()

    ' ==========================================
    ' 6. SOLIDIFICATION
    ' ==========================================
    Dim shapeFactory
    Set shapeFactory = part1.ShapeFactory
    
    ' Hollow Main Tube
    part1.InWorkObject = part1.MainBody
    Dim thickMain
    Set thickMain = shapeFactory.AddNewThickSurface(finalSurfaceRef, 1, {main_thickness}, 0.0)
    
    ' Vertical Ribs Solid Body
    Dim body1 : Set body1 = part1.Bodies.Add() : body1.Name = "Body.1_Vertical_Ribs" : part1.InWorkObject = body1
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(vRibR))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(vRibL))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(vRibU))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(vRibD))
    
    ' Circular Ribs Solid Body
    Dim body2 : Set body2 = part1.Bodies.Add() : body2.Name = "Body.2_Circular_Ribs" : part1.InWorkObject = body2
    Dim j, shp
    For j = 1 To ribsSet.HybridShapes.Count
        Set shp = ribsSet.HybridShapes.Item(j)
        If InStr(shp.Name, "Circular_Rib_Sweep_") > 0 Then ' Note: Name check updated to match sweep naming
            shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(shp))
        End If
    Next

    part1.Update()

    ' Boolean Add
    part1.InWorkObject = part1.MainBody
    Dim addVert : Set addVert = shapeFactory.AddNewAdd(body1) : part1.UpdateObject addVert 
    Dim addCirc : Set addCirc = shapeFactory.AddNewAdd(body2) : part1.UpdateObject addCirc 

    part1.Update()
End Sub
"""

# --- 3. DOWNLOAD BUTTON ---
st.header("3. Generate & Download")
st.download_button(
    label="⬇️ Download CATIA Macro (.catvbs)",
    data=vbscript_code,
    file_name="MakeSegmentedTube.catvbs",
    mime="text/plain"
)
