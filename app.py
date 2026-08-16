import streamlit as st

st.set_page_config(page_title="CATIA Variable Tube Generator", page_icon="🚀", layout="wide")

st.title("🚀 CATIA V5: Variable Diameter Tube Generator")
st.write("This macro builds a Multi-Section loft using 7 varying circles, 4 guide curves, and merges all ribs into a solid part.")

# --- 1. USER INTERFACE ---
st.header("1. Global Tube Parameters")
col1, col2 = st.columns(2)
with col1:
    main_thickness = st.number_input("Main Tube Thickness (mm)", value=2.5, step=0.5)
    vert_rib_radius = st.number_input("Vertical Wire Radius (mm)", value=1.0, step=0.5)
with col2:
    circ_rib_radius = st.number_input("Circular Rib Radius (mm)", value=1.5, step=0.5)
    circ_rib_spacing = st.number_input("Circular Rib Spacing (mm)", value=20.0, step=5.0)

st.header("2. Spline Coordinates & Varying Radii (7 Points)")
points = []
for i in range(1, 8):
    cols = st.columns([1.5, 1, 1, 1, 1]) 
    default_x = [0.0, 0.0, 150.0, 300.0, 300.0, 150.0, 0.0]
    default_y = [0.0, 0.0, 0.0, 150.0, 300.0, 450.0, 450.0]
    default_z = [0.0, 200.0, 300.0, 300.0, 450.0, 600.0, 800.0]
    default_r = [30.0, 32.0, 38.0, 45.0, 38.0, 30.0, 25.0]
    
    with cols[0]:
        pt_id = st.text_input(f"P{i} ID", value=f"Point_{i}", key=f"id{i}")
    with cols[1]:
        x = st.number_input(f"P{i} X", value=default_x[i-1], key=f"x{i}")
    with cols[2]:
        y = st.number_input(f"P{i} Y", value=default_y[i-1], key=f"y{i}")
    with cols[3]:
        z = st.number_input(f"P{i} Z", value=default_z[i-1], key=f"z{i}")
    with cols[4]:
        r = st.number_input(f"P{i} Radius", value=default_r[i-1], key=f"r{i}")
    
    points.append((pt_id, x, y, z, r))

# --- 2. VBSCRIPT GENERATION LOGIC ---
vbscript_code = f"""Sub CATMain()
    Const PI = 3.141592653589793
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

    Dim spline
    Set spline = hsf.AddNewSpline()
    spline.SetSplineType 0
    spline.SetClosing 0

    ' ==========================================
    ' 1. CREATE CENTER SPLINE POINTS
    ' ==========================================
"""

for i, (p_id, px, py, pz, pr) in enumerate(points, start=1):
    vbscript_code += f"""    Dim pt{i}
    Set pt{i} = hsf.AddNewPointCoord({px}, {py}, {pz})
    pt{i}.Name = "{p_id}"
    geomSet.AppendHybridShape pt{i}
    Dim refPt{i}
    Set refPt{i} = part1.CreateReferenceFromObject(pt{i})
    spline.AddPoint refPt{i}
"""

vbscript_code += f"""
    geomSet.AppendHybridShape spline
    Dim splineRef
    Set splineRef = part1.CreateReferenceFromObject(spline)

    ' ==========================================
    ' 2. CREATE PLANES, CIRCLES & 4 POINTS EACH
    ' ==========================================
"""

for i, (p_id, px, py, pz, pr) in enumerate(points, start=1):
    vbscript_code += f"""    ' --- Section {i} ---
    Dim plane{i}
    Set plane{i} = hsf.AddNewPlaneNormal(splineRef, refPt{i})
    geomSet.AppendHybridShape plane{i}
    Dim refPlane{i} : Set refPlane{i} = part1.CreateReferenceFromObject(plane{i})

    Dim circle{i}
    Set circle{i} = hsf.AddNewCircleCtrRad(refPt{i}, refPlane{i}, False, {pr})
    geomSet.AppendHybridShape circle{i}
    Dim refCircle{i} : Set refCircle{i} = part1.CreateReferenceFromObject(circle{i})

    ' Generate 4 points on the circle (0, 90, 180, 270 degrees via distance)
    Dim pt_c1_{i}, pt_c2_{i}, pt_c3_{i}, pt_c4_{i}
    
    Set pt_c1_{i} = hsf.AddNewPointOnCurveFromDistance(refCircle{i}, 0.0, False)
    geomSet.AppendHybridShape pt_c1_{i}
    Dim ref_pt_c1_{i} : Set ref_pt_c1_{i} = part1.CreateReferenceFromObject(pt_c1_{i})

    Set pt_c2_{i} = hsf.AddNewPointOnCurveFromDistance(refCircle{i}, (PI * {pr} / 2.0), False)
    geomSet.AppendHybridShape pt_c2_{i}
    Dim ref_pt_c2_{i} : Set ref_pt_c2_{i} = part1.CreateReferenceFromObject(pt_c2_{i})

    Set pt_c3_{i} = hsf.AddNewPointOnCurveFromDistance(refCircle{i}, (PI * {pr}), False)
    geomSet.AppendHybridShape pt_c3_{i}
    Dim ref_pt_c3_{i} : Set ref_pt_c3_{i} = part1.CreateReferenceFromObject(pt_c3_{i})

    Set pt_c4_{i} = hsf.AddNewPointOnCurveFromDistance(refCircle{i}, (PI * {pr} * 1.5), False)
    geomSet.AppendHybridShape pt_c4_{i}
    Dim ref_pt_c4_{i} : Set ref_pt_c4_{i} = part1.CreateReferenceFromObject(pt_c4_{i})
"""

vbscript_code += f"""
    ' ==========================================
    ' 3. CREATE 4 GUIDE CURVES (SPLINES)
    ' ==========================================
"""

for g in range(1, 5):
    vbscript_code += f"""    Dim guide{g}
    Set guide{g} = hsf.AddNewSpline()
    guide{g}.SetSplineType 0
"""
    for i in range(1, 8):
        vbscript_code += f"    guide{g}.AddPoint ref_pt_c{g}_{i}\n"
        
    vbscript_code += f"""    geomSet.AppendHybridShape guide{g}
    Dim refGuide{g} : Set refGuide{g} = part1.CreateReferenceFromObject(guide{g})
"""

vbscript_code += f"""
    ' ==========================================
    ' 4. CREATE MULTI-SECTIONS SURFACE (LOFT)
    ' ==========================================
    Dim mainLoft
    Set mainLoft = hsf.AddNewLoft()
    mainLoft.SectionCoupling = 1 ' Ratio coupling
"""

for i in range(1, 8):
    vbscript_code += f"    mainLoft.AddSectionToLoft refCircle{i}, 1, ref_pt_c1_{i}\n"

for g in range(1, 5):
    vbscript_code += f"    mainLoft.AddGuide refGuide{g}\n"

vbscript_code += f"""    mainLoft.SetSpine splineRef
    mainLoft.Name = "Main_Tube_Loft"
    geomSet.AppendHybridShape mainLoft
    
    Dim sweepRef
    Set sweepRef = part1.CreateReferenceFromObject(mainLoft)

    ' ==========================================
    ' 5. VERTICAL RIBS (Swept along Guides)
    ' ==========================================
    Dim sweepRight, sweepLeft, sweepUp, sweepDown
    
    Set sweepRight = hsf.AddNewSweepCircle(refGuide1)
    sweepRight.Mode = 6 : sweepRight.SetRadius 1, {vert_rib_radius} : geomSet.AppendHybridShape sweepRight

    Set sweepLeft = hsf.AddNewSweepCircle(refGuide2)
    sweepLeft.Mode = 6 : sweepLeft.SetRadius 1, {vert_rib_radius} : geomSet.AppendHybridShape sweepLeft

    Set sweepUp = hsf.AddNewSweepCircle(refGuide3)
    sweepUp.Mode = 6 : sweepUp.SetRadius 1, {vert_rib_radius} : geomSet.AppendHybridShape sweepUp

    Set sweepDown = hsf.AddNewSweepCircle(refGuide4)
    sweepDown.Mode = 6 : sweepDown.SetRadius 1, {vert_rib_radius} : geomSet.AppendHybridShape sweepDown

    part1.Update()

    ' ==========================================
    ' 6. CIRCULAR RIBS (Intersection with Loft)
    ' ==========================================
    Dim TheSPAWorkbench
    Set TheSPAWorkbench = partDocument1.GetWorkbench("SPAWorkbench")
    Dim measurableSpline
    Set measurableSpline = TheSPAWorkbench.GetMeasurable(splineRef)
    
    Dim totalLength
    totalLength = measurableSpline.Length
    
    Dim currentDist
    currentDist = {circ_rib_spacing}
    Dim ribCounter
    ribCounter = 1

    Do While currentDist < (totalLength - 1.0)
        Dim ptOnCurve, ptOnCurveRef, planeNormal, planeNormalRef, circleIntersect, circleIntersectRef, ribSweep
        
        Set ptOnCurve = hsf.AddNewPointOnCurveFromDistance(splineRef, currentDist, True)
        ribsSet.AppendHybridShape ptOnCurve
        Set ptOnCurveRef = part1.CreateReferenceFromObject(ptOnCurve)

        Set planeNormal = hsf.AddNewPlaneNormal(splineRef, ptOnCurveRef)
        ribsSet.AppendHybridShape planeNormal
        Set planeNormalRef = part1.CreateReferenceFromObject(planeNormal)

        Set circleIntersect = hsf.AddNewIntersection(planeNormalRef, sweepRef)
        circleIntersect.Name = "Rib_Circle_" & CStr(ribCounter)
        ribsSet.AppendHybridShape circleIntersect
        Set circleIntersectRef = part1.CreateReferenceFromObject(circleIntersect)

        Set ribSweep = hsf.AddNewSweepCircle(circleIntersectRef)
        ribSweep.Mode = 6
        ribSweep.SetRadius 1, {circ_rib_radius}
        ribSweep.Name = "Circular_Rib_Sweep_" & CStr(ribCounter)
        ribsSet.AppendHybridShape ribSweep

        currentDist = currentDist + {circ_rib_spacing}
        ribCounter = ribCounter + 1
    Loop

    part1.Update()

    ' ==========================================
    ' 7. SOLIDIFICATION & BOOLEAN ADD
    ' ==========================================
    Dim shapeFactory
    Set shapeFactory = part1.ShapeFactory
    
    ' Hollow Main Tube
    part1.InWorkObject = part1.MainBody
    Dim thickMain
    Set thickMain = shapeFactory.AddNewThickSurface(sweepRef, 1, {main_thickness}, 0.0)
    
    ' Vertical Ribs Solid Body
    Dim body1
    Set body1 = part1.Bodies.Add()
    body1.Name = "Body.1_Vertical_Ribs"
    part1.InWorkObject = body1
    
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepRight))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepLeft))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepUp))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepDown))
    
    ' Circular Ribs Solid Body
    Dim body2
    Set body2 = part1.Bodies.Add()
    body2.Name = "Body.2_Circular_Ribs"
    part1.InWorkObject = body2
    
    Dim j, shp
    For j = 1 To ribsSet.HybridShapes.Count
        Set shp = ribsSet.HybridShapes.Item(j)
        If InStr(shp.Name, "Circular_Rib_Sweep_") > 0 Then
            shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(shp))
        End If
    Next

    part1.Update()

    ' Boolean ADD into MainBody
    part1.InWorkObject = part1.MainBody
    
    Dim addVert
    Set addVert = shapeFactory.AddNewAdd(body1)
    part1.UpdateObject addVert 
    
    Dim addCirc
    Set addCirc = shapeFactory.AddNewAdd(body2)
    part1.UpdateObject addCirc 

    part1.Update()
End Sub
"""

# --- 3. DOWNLOAD BUTTON ---
st.header("3. Generate & Download")
st.download_button(
    label="⬇️ Download CATIA Macro (.catvbs)",
    data=vbscript_code,
    file_name="MakeVariableTube.catvbs",
    mime="text/plain"
)
