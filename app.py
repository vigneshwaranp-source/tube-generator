import streamlit as st

st.set_page_config(page_title="CATIA Spline-Driven Tube Generator", page_icon="🚀", layout="wide")

st.title("🚀 CATIA V5: Spline-Driven Tube & 2D Drawing Generator")
st.write("This macro builds a smooth variable tube strictly following the 3D Spline via a Multi-Section Loft, complete with solid ribs and automated 2D drafting.")

# --- 1. USER INTERFACE ---
st.header("1. Global Tube Parameters")
col1, col2, col3 = st.columns(3)
with col1:
    main_thickness = st.number_input("Main Tube Thickness (mm)", value=2.5, step=0.5)
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

st.header("3. Automation Options")
generate_drawing = st.checkbox("Generate 2D Drawing (Front & Isometric Views)", value=True)

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

    ' ==========================================
    ' 1. CREATE CENTER SPLINE POINTS & SPLINE
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
    Dim spline
    Set spline = hsf.AddNewSpline()
    spline.SetSplineType 0
    spline.SetClosing 0
"""
for i in range(1, 8):
    vbscript_code += f"    spline.AddPoint refPt{i}\n"

vbscript_code += f"""    geomSet.AppendHybridShape spline
    Dim splineRef : Set splineRef = part1.CreateReferenceFromObject(spline)

    ' ==========================================
    ' 2. CREATE PLANES, CIRCLES & QUADRANT POINTS
    ' ==========================================
"""

for i, (p_id, px, py, pz, pr) in enumerate(points, start=1):
    vbscript_code += f"""    ' --- Section {i} ---
    Dim plane{i} : Set plane{i} = hsf.AddNewPlaneNormal(splineRef, refPt{i}) : geomSet.AppendHybridShape plane{i}
    Dim refPlane{i} : Set refPlane{i} = part1.CreateReferenceFromObject(plane{i})

    Dim circle{i} : Set circle{i} = hsf.AddNewCircleCtrRad(refPt{i}, refPlane{i}, False, {pr}) : geomSet.AppendHybridShape circle{i}
    Dim refCircle{i} : Set refCircle{i} = part1.CreateReferenceFromObject(circle{i})

    ' Generate 4 points on the circle via distance (0, 90, 180, 270 degrees)
    Dim pt_c1_{i} : Set pt_c1_{i} = hsf.AddNewPointOnCurveFromDistance(refCircle{i}, 0.0, False) : geomSet.AppendHybridShape pt_c1_{i}
    Dim ref_pt_c1_{i} : Set ref_pt_c1_{i} = part1.CreateReferenceFromObject(pt_c1_{i})

    Dim pt_c2_{i} : Set pt_c2_{i} = hsf.AddNewPointOnCurveFromDistance(refCircle{i}, (PI * {pr} / 2.0), False) : geomSet.AppendHybridShape pt_c2_{i}
    Dim ref_pt_c2_{i} : Set ref_pt_c2_{i} = part1.CreateReferenceFromObject(pt_c2_{i})

    Dim pt_c3_{i} : Set pt_c3_{i} = hsf.AddNewPointOnCurveFromDistance(refCircle{i}, (PI * {pr}), False) : geomSet.AppendHybridShape pt_c3_{i}
    Dim ref_pt_c3_{i} : Set ref_pt_c3_{i} = part1.CreateReferenceFromObject(pt_c3_{i})

    Dim pt_c4_{i} : Set pt_c4_{i} = hsf.AddNewPointOnCurveFromDistance(refCircle{i}, (PI * {pr} * 1.5), False) : geomSet.AppendHybridShape pt_c4_{i}
    Dim ref_pt_c4_{i} : Set ref_pt_c4_{i} = part1.CreateReferenceFromObject(pt_c4_{i})
"""

vbscript_code += f"""
    ' ==========================================
    ' 3. CREATE 4 VERTICAL RIB PATHS (SPLINES)
    ' ==========================================
"""

for g in range(1, 5):
    vbscript_code += f"""    Dim guide{g} : Set guide{g} = hsf.AddNewSpline() : guide{g}.SetSplineType 0\n"""
    for i in range(1, 8):
        vbscript_code += f"    guide{g}.AddPoint ref_pt_c{g}_{i}\n"
    vbscript_code += f"""    geomSet.AppendHybridShape guide{g}
    Dim refGuide{g} : Set refGuide{g} = part1.CreateReferenceFromObject(guide{g})
"""

vbscript_code += f"""
    ' ==========================================
    ' 4. CREATE SPLINE-DRIVEN LOFT (No Guides!)
    ' ==========================================
    Dim mainLoft
    Set mainLoft = hsf.AddNewLoft()
    mainLoft.SectionCoupling = 1
"""

# Add sections using Point 1 as the closing point to prevent twist, but DO NOT add guides.
for i in range(1, 8):
    vbscript_code += f"    mainLoft.AddSectionToLoft refCircle{i}, 1, ref_pt_c1_{i}\n"

vbscript_code += f"""    mainLoft.SetSpine splineRef
    mainLoft.Name = "Main_Tube_Loft"
    geomSet.AppendHybridShape mainLoft
    
    Dim finalSurfaceRef : Set finalSurfaceRef = part1.CreateReferenceFromObject(mainLoft)
    part1.Update()

    ' ==========================================
    ' 5. VERTICAL & CIRCULAR RIBS 
    ' ==========================================
    ' Sweep ribs strictly along the 4 wire paths
    Dim vRib1 : Set vRib1 = hsf.AddNewSweepCircle(refGuide1) : vRib1.Mode = 6 : vRib1.SetRadius 1, {vert_rib_radius} : geomSet.AppendHybridShape vRib1
    Dim vRib2 : Set vRib2 = hsf.AddNewSweepCircle(refGuide2) : vRib2.Mode = 6 : vRib2.SetRadius 1, {vert_rib_radius} : geomSet.AppendHybridShape vRib2
    Dim vRib3 : Set vRib3 = hsf.AddNewSweepCircle(refGuide3) : vRib3.Mode = 6 : vRib3.SetRadius 1, {vert_rib_radius} : geomSet.AppendHybridShape vRib3
    Dim vRib4 : Set vRib4 = hsf.AddNewSweepCircle(refGuide4) : vRib4.Mode = 6 : vRib4.SetRadius 1, {vert_rib_radius} : geomSet.AppendHybridShape vRib4

    ' Circular Ribs driven perfectly along the main spline
    Dim TheSPAWorkbench : Set TheSPAWorkbench = partDocument1.GetWorkbench("SPAWorkbench")
    Dim measurableSpline : Set measurableSpline = TheSPAWorkbench.GetMeasurable(splineRef)
    Dim totalLength : totalLength = measurableSpline.Length
    Dim currentDist : currentDist = {circ_rib_spacing}
    Dim ribCounter : ribCounter = 1

    Do While currentDist < (totalLength - 1.0)
        Dim ptOnCurve : Set ptOnCurve = hsf.AddNewPointOnCurveFromDistance(splineRef, currentDist, True) : ribsSet.AppendHybridShape ptOnCurve
        Dim planeNormal : Set planeNormal = hsf.AddNewPlaneNormal(splineRef, part1.CreateReferenceFromObject(ptOnCurve)) : ribsSet.AppendHybridShape planeNormal
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
    
    part1.InWorkObject = part1.MainBody
    Dim thickMain
    Set thickMain = shapeFactory.AddNewThickSurface(finalSurfaceRef, 1, {main_thickness}, 0.0)
    
    Dim body1 : Set body1 = part1.Bodies.Add() : body1.Name = "Body.1_Vertical_Ribs" : part1.InWorkObject = body1
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(vRib1))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(vRib2))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(vRib3))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(vRib4))
    
    Dim body2 : Set body2 = part1.Bodies.Add() : body2.Name = "Body.2_Circular_Ribs" : part1.InWorkObject = body2
    Dim j, shp
    For j = 1 To ribsSet.HybridShapes.Count
        Set shp = ribsSet.HybridShapes.Item(j)
        If InStr(shp.Name, "Rib_Circle_") > 0 And InStr(shp.Name, "Sweep") = 0 Then
            ' Skip the intersection curves, we only want to close the sweep surfaces
        ElseIf InStr(shp.Name, "Sweep") > 0 Then 
            shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(shp))
        End If
    Next

    part1.Update()

    part1.InWorkObject = part1.MainBody
    Dim addVert : Set addVert = shapeFactory.AddNewAdd(body1) : part1.UpdateObject addVert 
    Dim addCirc : Set addCirc = shapeFactory.AddNewAdd(body2) : part1.UpdateObject addCirc 

    part1.Update()
"""

if generate_drawing:
    vbscript_code += f"""
    ' ==========================================
    ' 7. 2D DRAFTING AUTOMATION
    ' ==========================================
    Dim drawingDoc
    Set drawingDoc = CATIA.Documents.Add("Drawing")
    
    Dim drawingSheets
    Set drawingSheets = drawingDoc.Sheets
    Dim activeSheet
    Set activeSheet = drawingSheets.ActiveSheet
    
    Dim drawingViews
    Set drawingViews = activeSheet.Views
    
    ' -- Front View --
    Dim frontView
    Set frontView = drawingViews.Add("AutomaticNaming")
    
    Dim frontViewGen
    Set frontViewGen = frontView.GenerativeBehavior
    frontViewGen.Document = partDocument1
    frontViewGen.DefineFrontView 1, 0, 0, 0, 0, 1
    
    frontView.X = 150
    frontView.Y = 150
    frontView.Scale2 = 0.2 
    
    ' -- Isometric View --
    Dim isoView
    Set isoView = drawingViews.Add("AutomaticNaming")
    
    Dim isoViewGen
    Set isoViewGen = isoView.GenerativeBehavior
    isoViewGen.Document = partDocument1
    isoViewGen.DefineIsometricView 0.707, 0.707, 0.707, 0, 0, 1
    
    isoView.X = 400
    isoView.Y = 150
    isoView.Scale2 = 0.2
    
    frontViewGen.Update()
    isoViewGen.Update()
"""

vbscript_code += "\nEnd Sub"

# --- 4. DOWNLOAD BUTTON ---
st.header("4. Generate & Download")
st.download_button(
    label="⬇️ Download CATIA Macro (.catvbs)",
    data=vbscript_code,
    file_name="MakeSplineTube.catvbs",
    mime="text/plain"
)
