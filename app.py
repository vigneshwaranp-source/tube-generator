import streamlit as st

st.set_page_config(page_title="CATIA Ribbed Tube Generator", page_icon="⚙️", layout="wide")

st.title("⚙️ CATIA V5: Freeflow Loft & Solid Rib Generator")
st.write("This app generates a highly robust CATIA macro. It uses the Natural Freeflow Loft, domain-filtered circular intersections, and automatically builds the solid Boolean PartBody.")

# --- 1. USER INTERFACE ---
st.header("1. Tube Parameters")
col1, col2 = st.columns(2)
with col1:
    main_thickness = st.number_input("Main Tube Thickness (mm)", value=2.5, step=0.5)
    vert_rib_radius = st.number_input("Vertical Wire Radius (mm)", value=2.0, step=0.5) # Defaults to 4mm Dia
with col2:
    circ_rib_radius = st.number_input("Circular Rib Radius (mm)", value=2.0, step=0.5) # Defaults to 4mm Dia
    circ_rib_spacing = st.number_input("Circular Rib Spacing (mm)", value=30.0, step=5.0)

st.header("2. Spline Coordinates & Radii (7 Points)")
points = []
for i in range(1, 8):
    cols = st.columns([1.5, 1, 1, 1, 1]) 
    default_x = [0.0, 150.0, 300.0, 150.0, -100.0, -200.0, 0.0]
    default_y = [0.0, 150.0, -50.0, -250.0, -100.0, 150.0, 300.0]
    default_z = [0.0, 150.0, 300.0, 450.0, 600.0, 750.0, 900.0]
    default_r = [25.0, 50.0, 20.0, 60.0, 30.0, 55.0, 25.0]
    
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
vbscript_code = """Sub CATMain()
    Dim partDocument1
    
    ' ==========================================
    ' SMART DOCUMENT CHECK
    ' ==========================================
    On Error Resume Next
    Set partDocument1 = CATIA.ActiveDocument
    On Error GoTo 0
    
    If IsEmpty(partDocument1) Or partDocument1 Is Nothing Then
        Set partDocument1 = CATIA.Documents.Add("Part")
    End If
    
    If TypeName(partDocument1) <> "PartDocument" Then
        MsgBox "Please open a Part Document and try again.", vbCritical, "Wrong Document Type"
        Exit Sub
    End If
    
    Dim part1: Set part1 = partDocument1.Part
    Dim hsf: Set hsf = part1.HybridShapeFactory
    Dim hybridBodies1: Set hybridBodies1 = part1.HybridBodies
    
    ' ==========================================
    ' GEOMETRICAL SETS
    ' ==========================================
    Dim geomSet: Set geomSet = hybridBodies1.Add(): geomSet.Name = "Macro_Tube_Geometry"
    Dim linesSet: Set linesSet = hybridBodies1.Add(): linesSet.Name = "Vertical_Lines"
    Dim circLinesSet: Set circLinesSet = hybridBodies1.Add(): circLinesSet.Name = "Circular_Lines"

    Dim spline: Set spline = hsf.AddNewSpline(): spline.SetSplineType 0: spline.SetClosing 0
"""

# Dynamically generate points
for i, (p_id, px, py, pz, pr) in enumerate(points, start=1):
    vbscript_code += f"""
    Dim pt{i}: Set pt{i} = hsf.AddNewPointCoord({px}, {py}, {pz}): pt{i}.Name = "{p_id}": geomSet.AppendHybridShape pt{i}
    Dim ref{i}: Set ref{i} = part1.CreateReferenceFromObject(pt{i}): spline.AddPoint ref{i}
"""

vbscript_code += """
    geomSet.AppendHybridShape spline
    Dim splineRef: Set splineRef = part1.CreateReferenceFromObject(spline)

    ' ==========================================
    ' PLANES, CIRCLES & CLOSING POINTS
    ' ==========================================
    Dim dirY: Set dirY = hsf.AddNewDirectionByCoord(0, 1, 0)
"""

# Dynamically generate profiles
for i, (p_id, px, py, pz, pr) in enumerate(points, start=1):
    vbscript_code += f"""
    Dim plane{i}: Set plane{i} = hsf.AddNewPlaneNormal(splineRef, ref{i}): geomSet.AppendHybridShape plane{i}
    Dim refPlane{i}: Set refPlane{i} = part1.CreateReferenceFromObject(plane{i})
    Dim circle{i}: Set circle{i} = hsf.AddNewCircleCtrRad(ref{i}, refPlane{i}, True, {pr}): geomSet.AppendHybridShape circle{i}
    Dim refCircle{i}: Set refCircle{i} = part1.CreateReferenceFromObject(circle{i})
    Dim closePt{i}: Set closePt{i} = hsf.AddNewExtremum(refCircle{i}, dirY, 1): geomSet.AppendHybridShape closePt{i}
    Dim refClosePt{i}: Set refClosePt{i} = part1.CreateReferenceFromObject(closePt{i})
"""

vbscript_code += f"""
    ' ==========================================
    ' MAIN TUBE LOFT (Freeflow)
    ' ==========================================
    Dim mainLoft: Set mainLoft = hsf.AddNewLoft()
    mainLoft.SectionCoupling = 1
"""

for i in range(1, 8):
    vbscript_code += f"    mainLoft.AddSectionToLoft refCircle{i}, 1, refClosePt{i}\n"

vbscript_code += f"""
    mainLoft.Name = "Main_Tube_Surface"
    geomSet.AppendHybridShape mainLoft
    Dim sweepRef: Set sweepRef = part1.CreateReferenceFromObject(mainLoft)

    ' ==========================================
    ' VERTICAL RIBS (Intersections + Sweeps)
    ' ==========================================
    Dim dirNY: Set dirNY = hsf.AddNewDirectionByCoord(0, -1, 0)
    Dim dirX: Set dirX = hsf.AddNewDirectionByCoord(1, 0, 0)
    Dim dirNX: Set dirNX = hsf.AddNewDirectionByCoord(-1, 0, 0)

    Dim lnU: Set lnU = hsf.AddNewLinePtDir(ref1, dirY, 0.0, 150.0, False): linesSet.AppendHybridShape lnU
    Dim lnD: Set lnD = hsf.AddNewLinePtDir(ref1, dirNY, 0.0, 150.0, False): linesSet.AppendHybridShape lnD
    Dim lnR: Set lnR = hsf.AddNewLinePtDir(ref1, dirX, 0.0, 150.0, False): linesSet.AppendHybridShape lnR
    Dim lnL: Set lnL = hsf.AddNewLinePtDir(ref1, dirNX, 0.0, 150.0, False): linesSet.AppendHybridShape lnL

    Dim ribbonU: Set ribbonU = hsf.AddNewSweepExplicit(part1.CreateReferenceFromObject(lnU), splineRef): linesSet.AppendHybridShape ribbonU
    Dim ribbonD: Set ribbonD = hsf.AddNewSweepExplicit(part1.CreateReferenceFromObject(lnD), splineRef): linesSet.AppendHybridShape ribbonD
    Dim ribbonR: Set ribbonR = hsf.AddNewSweepExplicit(part1.CreateReferenceFromObject(lnR), splineRef): linesSet.AppendHybridShape ribbonR
    Dim ribbonL: Set ribbonL = hsf.AddNewSweepExplicit(part1.CreateReferenceFromObject(lnL), splineRef): linesSet.AppendHybridShape ribbonL

    Dim crvU: Set crvU = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonU), sweepRef): crvU.Name = "Surface_Line_Top": linesSet.AppendHybridShape crvU
    Dim crvD: Set crvD = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonD), sweepRef): crvD.Name = "Surface_Line_Bottom": linesSet.AppendHybridShape crvD
    Dim crvR: Set crvR = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonR), sweepRef): crvR.Name = "Surface_Line_Right": linesSet.AppendHybridShape crvR
    Dim crvL: Set crvL = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonL), sweepRef): crvL.Name = "Surface_Line_Left": linesSet.AppendHybridShape crvL

    Dim sweepU: Set sweepU = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(crvU)): sweepU.Mode = 6: sweepU.SetRadius 1, {vert_rib_radius}: sweepU.Name = "Sweep_Top": linesSet.AppendHybridShape sweepU
    Dim sweepD: Set sweepD = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(crvD)): sweepD.Mode = 6: sweepD.SetRadius 1, {vert_rib_radius}: sweepD.Name = "Sweep_Bottom": linesSet.AppendHybridShape sweepD
    Dim sweepR: Set sweepR = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(crvR)): sweepR.Mode = 6: sweepR.SetRadius 1, {vert_rib_radius}: sweepR.Name = "Sweep_Right": linesSet.AppendHybridShape sweepR
    Dim sweepL: Set sweepL = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(crvL)): sweepL.Mode = 6: sweepL.SetRadius 1, {vert_rib_radius}: sweepL.Name = "Sweep_Left": linesSet.AppendHybridShape sweepL

    ' ==========================================
    ' CIRCULAR RIBS (Equal Division + Multi-Domain Near Fix)
    ' ==========================================
    part1.Update()
    
    Dim TheSPAWorkbench
    Set TheSPAWorkbench = partDocument1.GetWorkbench("SPAWorkbench")
    Dim measurableSpline
    Set measurableSpline = TheSPAWorkbench.GetMeasurable(splineRef)
    
    Dim totalLength
    totalLength = measurableSpline.Length
    
    Dim targetSpacing
    targetSpacing = {circ_rib_spacing} 
    
    Dim numDivisions
    numDivisions = Int(totalLength / targetSpacing)
    
    Dim exactSpacing
    exactSpacing = totalLength / numDivisions
    
    Dim i
    For i = 1 To (numDivisions - 1)
        Dim currentDist
        currentDist = i * exactSpacing
        
        Dim ptOnCurve, ptOnCurveRef, planeNormal, planeNormalRef, rawIntersect
        
        Set ptOnCurve = hsf.AddNewPointOnCurveFromDistance(splineRef, currentDist, True)
        ptOnCurve.Name = "Point_at_" & CStr(Round(currentDist, 1)) & "mm"
        circLinesSet.AppendHybridShape ptOnCurve
        Set ptOnCurveRef = part1.CreateReferenceFromObject(ptOnCurve)

        Set planeNormal = hsf.AddNewPlaneNormal(splineRef, ptOnCurveRef)
        planeNormal.Name = "Normal_Plane_" & CStr(i)
        circLinesSet.AppendHybridShape planeNormal
        Set planeNormalRef = part1.CreateReferenceFromObject(planeNormal)

        Set rawIntersect = hsf.AddNewIntersection(planeNormalRef, sweepRef)
        
        Dim nearIntersect
        Set nearIntersect = hsf.AddNewNear(part1.CreateReferenceFromObject(rawIntersect), ptOnCurveRef)
        nearIntersect.Name = "Circ_Intersection_" & CStr(i)
        circLinesSet.AppendHybridShape nearIntersect
        
        Dim circSweep
        Set circSweep = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(nearIntersect))
        circSweep.Mode = 6
        circSweep.SetRadius 1, {circ_rib_radius}
        circSweep.Name = "Circ_Sweep_" & CStr(i)
        circLinesSet.AppendHybridShape circSweep
    Next
    
    part1.Update()

    ' ==========================================
    ' SOLIDIFICATION
    ' ==========================================
    Dim shapeFactory
    Set shapeFactory = part1.ShapeFactory
    
    part1.InWorkObject = part1.MainBody
    Dim thickMain
    Set thickMain = shapeFactory.AddNewThickSurface(sweepRef, 1, {main_thickness}, 0.0)
    
    Dim bodyVert
    Set bodyVert = part1.Bodies.Add()
    bodyVert.Name = "Body.1_Vertical_Ribs"
    part1.InWorkObject = bodyVert
    
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepU))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepD))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepR))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepL))
    
    Dim bodyCirc
    Set bodyCirc = part1.Bodies.Add()
    bodyCirc.Name = "Body.2_Circular_Ribs"
    part1.InWorkObject = bodyCirc
    
    Dim j, shp
    For j = 1 To circLinesSet.HybridShapes.Count
        Set shp = circLinesSet.HybridShapes.Item(j)
        If InStr(shp.Name, "Circ_Sweep_") > 0 Then
            shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(shp))
        End If
    Next

    part1.Update()

    ' ==========================================
    ' BOOLEAN ASSEMBLY
    ' ==========================================
    part1.InWorkObject = part1.MainBody
    
    Dim addVert
    Set addVert = shapeFactory.AddNewAdd(bodyVert)
    part1.UpdateObject addVert
    
    Dim addCirc
    Set addCirc = shapeFactory.AddNewAdd(bodyCirc)
    part1.UpdateObject addCirc

    part1.Update()
End Sub
"""

# --- 3. DOWNLOAD BUTTON ---
st.header("3. Generate & Download")
st.download_button(
    label="⬇️ Download CATIA Macro (.catvbs)",
    data=vbscript_code,
    file_name="Master_Ribbed_Tube.catvbs",
    mime="text/plain"
)
