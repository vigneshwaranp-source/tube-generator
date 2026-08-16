import streamlit as st

st.set_page_config(page_title="CATIA Ribbed Tube Generator", page_icon="⚙️")

st.title("⚙️ CATIA V5: Ribbed Tube Macro Generator")
st.write("Enter your parameters below to generate a custom `.catvbs` macro file.")

# --- 1. USER INTERFACE ---
st.header("1. Tube Parameters")
col1, col2 = st.columns(2)
with col1:
    main_radius = st.number_input("Main Tube Radius (mm)", value=30.0, step=1.0)
    main_thickness = st.number_input("Main Tube Thickness (mm)", value=2.5, step=0.5)
with col2:
    vert_rib_radius = st.number_input("Vertical Wire Radius (mm)", value=1.0, step=0.5)
    circ_rib_radius = st.number_input("Circular Rib Radius (mm)", value=1.5, step=0.5)
    circ_rib_spacing = st.number_input("Circular Rib Spacing (mm)", value=20.0, step=5.0)

st.header("2. Spline Coordinates (7 Points)")
points = []
for i in range(1, 8):
    cols = st.columns(3)
    default_x = [0.0, 0.0, 150.0, 300.0, 300.0, 150.0, 0.0]
    default_y = [0.0, 0.0, 0.0, 150.0, 300.0, 450.0, 450.0]
    default_z = [0.0, 200.0, 300.0, 300.0, 450.0, 600.0, 800.0]
    
    with cols[0]:
        x = st.number_input(f"P{i} X", value=default_x[i-1], key=f"x{i}")
    with cols[1]:
        y = st.number_input(f"P{i} Y", value=default_y[i-1], key=f"y{i}")
    with cols[2]:
        z = st.number_input(f"P{i} Z", value=default_z[i-1], key=f"z{i}")
    points.append((x, y, z))

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

    Dim spline
    Set spline = hsf.AddNewSpline()
    spline.SetSplineType 0
    spline.SetClosing 0

    ' --- Points ---
"""

for i, (px, py, pz) in enumerate(points, start=1):
    vbscript_code += f"""    Dim pt{i}
    Set pt{i} = hsf.AddNewPointCoord({px}, {py}, {pz})
    pt{i}.Name = "Point_{i}"
    geomSet.AppendHybridShape pt{i}
    Dim ref{i}
    Set ref{i} = part1.CreateReferenceFromObject(pt{i})
    spline.AddPoint ref{i}
"""

vbscript_code += f"""
    ' --- Main Sweep ---
    geomSet.AppendHybridShape spline
    Dim splineRef
    Set splineRef = part1.CreateReferenceFromObject(spline)

    Dim mainSweep
    Set mainSweep = hsf.AddNewSweepCircle(splineRef)
    mainSweep.Mode = 6
    mainSweep.SetRadius 1, {main_radius}
    mainSweep.Name = "Main_Tube_Sweep"
    geomSet.AppendHybridShape mainSweep
    
    Dim sweepRef
    Set sweepRef = part1.CreateReferenceFromObject(mainSweep)

    ' --- 4 Vertical Wires ---
    Dim dirRight, dirLeft, dirUp, dirDown
    Set dirRight = hsf.AddNewDirectionByCoord(1, 0, 0)
    Set dirLeft = hsf.AddNewDirectionByCoord(-1, 0, 0)
    Set dirUp = hsf.AddNewDirectionByCoord(0, 1, 0)
    Set dirDown = hsf.AddNewDirectionByCoord(0, -1, 0)

    Dim lineRight, ribbonRight, curveRight, sweepRight
    Set lineRight = hsf.AddNewLinePtDir(ref1, dirRight, 0.0, 50.0, False): geomSet.AppendHybridShape lineRight
    Set ribbonRight = hsf.AddNewSweepExplicit(part1.CreateReferenceFromObject(lineRight), splineRef): geomSet.AppendHybridShape ribbonRight
    Set curveRight = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonRight), sweepRef): curveRight.Name = "Wire_Path_Right": geomSet.AppendHybridShape curveRight
    Set sweepRight = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(curveRight)): sweepRight.Mode = 6: sweepRight.SetRadius 1, {vert_rib_radius}: geomSet.AppendHybridShape sweepRight

    Dim lineLeft, ribbonLeft, curveLeft, sweepLeft
    Set lineLeft = hsf.AddNewLinePtDir(ref1, dirLeft, 0.0, 50.0, False): geomSet.AppendHybridShape lineLeft
    Set ribbonLeft = hsf.AddNewSweepExplicit(part1.CreateReferenceFromObject(lineLeft), splineRef): geomSet.AppendHybridShape ribbonLeft
    Set curveLeft = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonLeft), sweepRef): curveLeft.Name = "Wire_Path_Left": geomSet.AppendHybridShape curveLeft
    Set sweepLeft = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(curveLeft)): sweepLeft.Mode = 6: sweepLeft.SetRadius 1, {vert_rib_radius}: geomSet.AppendHybridShape sweepLeft

    Dim lineUp, ribbonUp, curveUp, sweepUp
    Set lineUp = hsf.AddNewLinePtDir(ref1, dirUp, 0.0, 50.0, False): geomSet.AppendHybridShape lineUp
    Set ribbonUp = hsf.AddNewSweepExplicit(part1.CreateReferenceFromObject(lineUp), splineRef): geomSet.AppendHybridShape ribbonUp
    Set curveUp = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonUp), sweepRef): curveUp.Name = "Wire_Path_Up": geomSet.AppendHybridShape curveUp
    Set sweepUp = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(curveUp)): sweepUp.Mode = 6: sweepUp.SetRadius 1, {vert_rib_radius}: geomSet.AppendHybridShape sweepUp

    Dim lineDown, ribbonDown, curveDown, sweepDown
    Set lineDown = hsf.AddNewLinePtDir(ref1, dirDown, 0.0, 50.0, False): geomSet.AppendHybridShape lineDown
    Set ribbonDown = hsf.AddNewSweepExplicit(part1.CreateReferenceFromObject(lineDown), splineRef): geomSet.AppendHybridShape ribbonDown
    Set curveDown = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonDown), sweepRef): curveDown.Name = "Wire_Path_Down": geomSet.AppendHybridShape curveDown
    Set sweepDown = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(curveDown)): sweepDown.Mode = 6: sweepDown.SetRadius 1, {vert_rib_radius}: geomSet.AppendHybridShape sweepDown

    ' --- Force Update Before Measuring ---
    part1.Update()

    ' --- Circular Ribs Loop ---
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

    ' --- Solidification ---
    Dim shapeFactory
    Set shapeFactory = part1.ShapeFactory
    
    part1.InWorkObject = part1.MainBody
    Dim thickMain
    Set thickMain = shapeFactory.AddNewThickSurface(sweepRef, 1, {main_thickness}, 0.0)
    
    Dim body1
    Set body1 = part1.Bodies.Add()
    body1.Name = "Body.1_Vertical_Ribs"
    part1.InWorkObject = body1
    
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepRight))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepLeft))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepUp))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepDown))
    
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
End Sub
"""

# --- 3. DOWNLOAD BUTTON ---
st.header("3. Generate & Download")
st.download_button(
    label="⬇️ Download CATIA Macro (.catvbs)",
    data=vbscript_code,
    file_name="MakeTube.catvbs",
    mime="text/plain"
)
