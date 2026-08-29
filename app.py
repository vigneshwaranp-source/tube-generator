import streamlit as st
import math

st.set_page_config(page_title="CATIA Ribbed Tube Generator", page_icon="⚙️", layout="wide")

st.title("⚙️ CATIA V5: Realistic Ribbed Hose Generator")
st.write("Enter DIAMETERS below. The app converts them to radii, applies domain filters, generates the solid body, and hides all construction geometry.")

# --- 1. USER INTERFACE ---
st.header("1. Tube Parameters")
col1, col2 = st.columns(2)
with col1:
    main_thickness = st.number_input("Main Tube Thickness (mm)", value=3.5, step=0.5)
    vert_rib_dia = st.number_input("Vertical Wire Diameter (mm)", value=3.8, step=0.2) 
with col2:
    circ_rib_dia = st.number_input("Circular Rib Diameter (mm)", value=4.0, step=0.2) 
    circ_rib_spacing = st.number_input("Circular Rib Spacing (mm)", value=30.0, step=5.0)

st.header("2. Spline Coordinates & Main Tube Diameters")
num_points = st.slider("Select Number of Spline Points (Minimum 3, Maximum 10)", min_value=3, max_value=10, value=7)

st.write("Default coordinates represent a realistic, gentle 3D automotive hose bend.")
points = []

default_x = [0.0, 0.0, 30.0, 100.0, 250.0, 400.0, 550.0, 700.0, 850.0, 1000.0]
default_y = [0.0, 0.0, 0.0, 50.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]
default_z = [0.0, 150.0, 300.0, 420.0, 500.0, 500.0, 500.0, 500.0, 500.0, 500.0]
default_d = [31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 37.0, 37.0, 37.0]

for i in range(1, num_points + 1):
    cols = st.columns([1.5, 1, 1, 1, 1]) 
    
    with cols[0]:
        pt_id = st.text_input(f"P{i} ID", value=f"Point_{i}", key=f"clean_id_{i}")
    with cols[1]:
        x = st.number_input(f"P{i} X", value=default_x[i-1], key=f"clean_x_{i}")
    with cols[2]:
        y = st.number_input(f"P{i} Y", value=default_y[i-1], key=f"clean_y_{i}")
    with cols[3]:
        z = st.number_input(f"P{i} Z", value=default_z[i-1], key=f"clean_z_{i}")
    with cols[4]:
        pd = st.number_input(f"P{i} Diameter", value=default_d[i-1], key=f"clean_d_{i}")
    
    points.append((pt_id, x, y, z, pd))

# --- 2. VECTOR MATH: 5MM STRAIGHT SECTION LOGIC ---
final_points = []
if len(points) >= 2:
    p1 = points[0]
    p2 = points[1]
    
    x1, y1, z1 = p1[1], p1[2], p1[3]
    x2, y2, z2 = p2[1], p2[2], p2[3]
    
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    final_points.append(p1) 
    
    if dist > 5.0:
        nx = x1 + 5.0 * ((x2 - x1) / dist)
        ny = y1 + 5.0 * ((y2 - y1) / dist)
        nz = z1 + 5.0 * ((z2 - z1) / dist)
        final_points.append(("Point_1_5mm_Offset", nx, ny, nz, p1[4]))
        
    final_points.extend(points[1:]) 
else:
    final_points = points

# --- 3. VBSCRIPT GENERATION LOGIC ---
vert_rib_rad = vert_rib_dia / 2.0
circ_rib_rad = circ_rib_dia / 2.0

if vert_rib_rad == circ_rib_rad:
    vert_rib_rad = vert_rib_rad - 0.05

vbscript_code = """Sub CATMain()
    Dim partDocument1
    
    If CATIA.Documents.Count = 0 Then
        Set partDocument1 = CATIA.Documents.Add("Part")
    Else
        Set partDocument1 = CATIA.ActiveDocument
    End If
    
    If TypeName(partDocument1) <> "PartDocument" Then
        MsgBox "Please open a Part Document and try again.", vbCritical, "Wrong Document Type"
        Exit Sub
    End If
    
    Dim part1: Set part1 = partDocument1.Part
    Dim hsf: Set hsf = part1.HybridShapeFactory
    Dim hybridBodies1: Set hybridBodies1 = part1.HybridBodies
    
    Dim geomSet: Set geomSet = hybridBodies1.Add(): geomSet.Name = "Macro_Tube_Geometry"
    Dim linesSet: Set linesSet = hybridBodies1.Add(): linesSet.Name = "Vertical_Lines"
    Dim circLinesSet: Set circLinesSet = hybridBodies1.Add(): circLinesSet.Name = "Circular_Lines"

    Dim spline: Set spline = hsf.AddNewSpline(): spline.SetSplineType 0: spline.SetClosing 0
"""

for i, (p_id, px, py, pz, pd) in enumerate(final_points, start=1):
    vbscript_code += f"""
    Dim pt{i}: Set pt{i} = hsf.AddNewPointCoord({px}, {py}, {pz}): pt{i}.Name = "{p_id}": geomSet.AppendHybridShape pt{i}
    Dim ref{i}: Set ref{i} = part1.CreateReferenceFromObject(pt{i}): spline.AddPoint ref{i}
"""

vbscript_code += """
    geomSet.AppendHybridShape spline
    Dim splineRef: Set splineRef = part1.CreateReferenceFromObject(spline)
    Dim dirY: Set dirY = hsf.AddNewDirectionByCoord(0, 1, 0)
"""

for i, (p_id, px, py, pz, pd) in enumerate(final_points, start=1):
    pr = pd / 2.0
    vbscript_code += f"""
    Dim plane{i}: Set plane{i} = hsf.AddNewPlaneNormal(splineRef, ref{i}): geomSet.AppendHybridShape plane{i}
    Dim refPlane{i}: Set refPlane{i} = part1.CreateReferenceFromObject(plane{i})
    Dim circle{i}: Set circle{i} = hsf.AddNewCircleCtrRad(ref{i}, refPlane{i}, True, {pr}): geomSet.AppendHybridShape circle{i}
    Dim refCircle{i}: Set refCircle{i} = part1.CreateReferenceFromObject(circle{i})
    Dim closePt{i}: Set closePt{i} = hsf.AddNewExtremum(refCircle{i}, dirY, 1): geomSet.AppendHybridShape closePt{i}
    Dim refClosePt{i}: Set refClosePt{i} = part1.CreateReferenceFromObject(closePt{i})
"""

vbscript_code += f"""
    Dim mainLoft: Set mainLoft = hsf.AddNewLoft()
    mainLoft.SectionCoupling = 1
"""

for i in range(1, len(final_points) + 1):
    vbscript_code += f"    mainLoft.AddSectionToLoft refCircle{i}, 1, refClosePt{i}\n"

vbscript_code += f"""
    mainLoft.Name = "Main_Tube_Surface"
    geomSet.AppendHybridShape mainLoft
    Dim sweepRef: Set sweepRef = part1.CreateReferenceFromObject(mainLoft)

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

    Dim rawU: Set rawU = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonU), sweepRef)
    Dim rawD: Set rawD = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonD), sweepRef)
    Dim rawR: Set rawR = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonR), sweepRef)
    Dim rawL: Set rawL = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonL), sweepRef)

    Dim crvU: Set crvU = hsf.AddNewNear(part1.CreateReferenceFromObject(rawU), ref1): crvU.Name = "Surface_Line_Top": linesSet.AppendHybridShape crvU
    Dim crvD: Set crvD = hsf.AddNewNear(part1.CreateReferenceFromObject(rawD), ref1): crvD.Name = "Surface_Line_Bottom": linesSet.AppendHybridShape crvD
    Dim crvR: Set crvR = hsf.AddNewNear(part1.CreateReferenceFromObject(rawR), ref1): crvR.Name = "Surface_Line_Right": linesSet.AppendHybridShape crvR
    Dim crvL: Set crvL = hsf.AddNewNear(part1.CreateReferenceFromObject(rawL), ref1): crvL.Name = "Surface_Line_Left": linesSet.AppendHybridShape crvL

    Dim sweepU: Set sweepU = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(crvU)): sweepU.Mode = 6: sweepU.SetRadius 1, {vert_rib_rad}: sweepU.Name = "Sweep_Top": linesSet.AppendHybridShape sweepU
    Dim sweepD: Set sweepD = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(crvD)): sweepD.Mode = 6: sweepD.SetRadius 1, {vert_rib_rad}: sweepD.Name = "Sweep_Bottom": linesSet.AppendHybridShape sweepD
    Dim sweepR: Set sweepR = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(crvR)): sweepR.Mode = 6: sweepR.SetRadius 1, {vert_rib_rad}: sweepR.Name = "Sweep_Right": linesSet.AppendHybridShape sweepR
    Dim sweepL: Set sweepL = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(crvL)): sweepL.Mode = 6: sweepL.SetRadius 1, {vert_rib_rad}: sweepL.Name = "Sweep_Left": linesSet.AppendHybridShape sweepL

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
        circSweep.SetRadius 1, {circ_rib_rad}
        circSweep.Name = "Circ_Sweep_" & CStr(i)
        circLinesSet.AppendHybridShape circSweep
    Next
    
    part1.Update()

    Dim shapeFactory
    Set shapeFactory = part1.ShapeFactory

    ' ==========================================
    ' STEP 1: CREATE MAIN OUTER BODY & ASSEMBLE
    ' ==========================================
    Dim bodyOuter
    Set bodyOuter = part1.Bodies.Add()
    bodyOuter.Name = "Body.Outer_Tube"
    part1.InWorkObject = bodyOuter
    
    Dim closeOuter
    Set closeOuter = shapeFactory.AddNewCloseSurface(sweepRef)
    part1.Update()
    
    part1.InWorkObject = part1.MainBody
    Dim assembleOuter
    Set assembleOuter = shapeFactory.AddNewAssemble(bodyOuter)
    part1.UpdateObject assembleOuter

    ' ==========================================
    ' STEP 2: CREATE RIBS & ASSEMBLE
    ' ==========================================
    Dim bodyVert
    Set bodyVert = part1.Bodies.Add()
    bodyVert.Name = "Body.Vertical_Ribs"
    part1.InWorkObject = bodyVert
    
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepU))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepD))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepR))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepL))
    
    Dim bodyCirc
    Set bodyCirc = part1.Bodies.Add()
    bodyCirc.Name = "Body.Circular_Ribs"
    part1.InWorkObject = bodyCirc
    
    Dim j, shp
    For j = 1 To circLinesSet.HybridShapes.Count
        Set shp = circLinesSet.HybridShapes.Item(j)
        If InStr(shp.Name, "Circ_Sweep_") > 0 Then
            shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(shp))
        End If
    Next

    part1.Update()
    
    part1.InWorkObject = part1.MainBody
    Dim assembleVert
    Set assembleVert = shapeFactory.AddNewAssemble(bodyVert)
    part1.UpdateObject assembleVert
    
    Dim assembleCirc
    Set assembleCirc = shapeFactory.AddNewAssemble(bodyCirc)
    part1.UpdateObject assembleCirc
    part1.Update()

    ' ==========================================
    ' STEP 3: CREATE INNER VOID CORE, COPY, PASTE WITH LINK, & THICKNESS
    ' ==========================================
    Dim bodyInner
    Set bodyInner = part1.Bodies.Add()
    bodyInner.Name = "Body.Inner_Void_Core"
    part1.Update()
    
    Dim sel
    Set sel = partDocument1.Selection
    sel.Clear()
    
    ' Fix: Explicitly grab the CloseSurface feature from the specification tree
    Dim targetClose
    Set targetClose = bodyOuter.Shapes.Item(1)
    
    sel.Add targetClose
    sel.Copy()
    sel.Clear()
    
    part1.InWorkObject = bodyInner
    sel.Add bodyInner
    sel.PasteSpecial "CATPrtResultWithLink"
    sel.Clear()
    
    ' Force CATIA to visually and memory-wise load the newly pasted solid
    part1.Update()
    
    ' Safety Check: Ensure the Solid successfully pasted before attempting thickness
    If bodyInner.Shapes.Count > 0 Then
        ' Grab the newly pasted solid (Solid.x)
        Dim pastedSolid
        Set pastedSolid = bodyInner.Shapes.Item(bodyInner.Shapes.Count)
        
        ' Select the pasted solid and search for all of its topological faces
        sel.Add pastedSolid
        sel.Search "Topology.CGMFace,sel"
        
        If sel.Count > 0 Then
            Dim firstFace
            Set firstFace = sel.Item(1).Reference
            
            Dim thickCore
            ' CORRECT API: AddNewThickness (Creates a 3D Thickness feature)
            ' A negative value shrinks the solid inwards
            Set thickCore = shapeFactory.AddNewThickness(firstFace, -{main_thickness})
            
            Dim fFace
            For fFace = 2 To sel.Count
                thickCore.AddFaceToThicken sel.Item(fFace).Reference
            Next
            
            part1.UpdateObject thickCore
        End If
        sel.Clear()
    End If
    
    ' NOTE: Body.Inner_Void_Core is left isolated and NOT removed from the main body.

    ' ==========================================
    ' 8. HIDE ALL CONSTRUCTION GEOMETRY
    ' ==========================================
    sel.Clear()
    sel.Add(geomSet)
    sel.Add(linesSet)
    sel.Add(circLinesSet)
    
    Dim visProperties1
    Set visProperties1 = sel.VisProperties
    visProperties1.SetShow 1
    
    sel.Clear()

End Sub
"""

# --- 4. DOWNLOAD BUTTON ---
st.header("3. Generate & Download")
st.download_button(
    label="⬇️ Download CATIA Macro (.catvbs)",
    data=vbscript_code,
    file_name="Master_Ribbed_Tube_Dynamic.catvbs",
    mime="text/plain"
)
