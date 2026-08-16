Sub CATMain()
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
    Dim pt1
    Set pt1 = hsf.AddNewPointCoord(0.0, 0.0, 0.0)
    pt1.Name = "31"
    geomSet.AppendHybridShape pt1
    Dim ref1
    Set ref1 = part1.CreateReferenceFromObject(pt1)
    spline.AddPoint ref1
    Dim pt2
    Set pt2 = hsf.AddNewPointCoord(0.0, 0.0, 200.0)
    pt2.Name = "32"
    geomSet.AppendHybridShape pt2
    Dim ref2
    Set ref2 = part1.CreateReferenceFromObject(pt2)
    spline.AddPoint ref2
    Dim pt3
    Set pt3 = hsf.AddNewPointCoord(150.0, 0.0, 300.0)
    pt3.Name = "33"
    geomSet.AppendHybridShape pt3
    Dim ref3
    Set ref3 = part1.CreateReferenceFromObject(pt3)
    spline.AddPoint ref3
    Dim pt4
    Set pt4 = hsf.AddNewPointCoord(300.0, 150.0, 300.0)
    pt4.Name = "34"
    geomSet.AppendHybridShape pt4
    Dim ref4
    Set ref4 = part1.CreateReferenceFromObject(pt4)
    spline.AddPoint ref4
    Dim pt5
    Set pt5 = hsf.AddNewPointCoord(300.0, 300.0, 450.0)
    pt5.Name = "35"
    geomSet.AppendHybridShape pt5
    Dim ref5
    Set ref5 = part1.CreateReferenceFromObject(pt5)
    spline.AddPoint ref5
    Dim pt6
    Set pt6 = hsf.AddNewPointCoord(150.0, 450.0, 600.0)
    pt6.Name = "36"
    geomSet.AppendHybridShape pt6
    Dim ref6
    Set ref6 = part1.CreateReferenceFromObject(pt6)
    spline.AddPoint ref6
    Dim pt7
    Set pt7 = hsf.AddNewPointCoord(0.0, 450.0, 800.0)
    pt7.Name = "Point_7"
    geomSet.AppendHybridShape pt7
    Dim ref7
    Set ref7 = part1.CreateReferenceFromObject(pt7)
    spline.AddPoint ref7

    ' --- Main Sweep ---
    geomSet.AppendHybridShape spline
    Dim splineRef
    Set splineRef = part1.CreateReferenceFromObject(spline)

    Dim mainSweep
    Set mainSweep = hsf.AddNewSweepCircle(splineRef)
    mainSweep.Mode = 6
    mainSweep.SetRadius 1, 30.0
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
    Set sweepRight = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(curveRight)): sweepRight.Mode = 6: sweepRight.SetRadius 1, 1.0: geomSet.AppendHybridShape sweepRight

    Dim lineLeft, ribbonLeft, curveLeft, sweepLeft
    Set lineLeft = hsf.AddNewLinePtDir(ref1, dirLeft, 0.0, 50.0, False): geomSet.AppendHybridShape lineLeft
    Set ribbonLeft = hsf.AddNewSweepExplicit(part1.CreateReferenceFromObject(lineLeft), splineRef): geomSet.AppendHybridShape ribbonLeft
    Set curveLeft = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonLeft), sweepRef): curveLeft.Name = "Wire_Path_Left": geomSet.AppendHybridShape curveLeft
    Set sweepLeft = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(curveLeft)): sweepLeft.Mode = 6: sweepLeft.SetRadius 1, 1.0: geomSet.AppendHybridShape sweepLeft

    Dim lineUp, ribbonUp, curveUp, sweepUp
    Set lineUp = hsf.AddNewLinePtDir(ref1, dirUp, 0.0, 50.0, False): geomSet.AppendHybridShape lineUp
    Set ribbonUp = hsf.AddNewSweepExplicit(part1.CreateReferenceFromObject(lineUp), splineRef): geomSet.AppendHybridShape ribbonUp
    Set curveUp = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonUp), sweepRef): curveUp.Name = "Wire_Path_Up": geomSet.AppendHybridShape curveUp
    Set sweepUp = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(curveUp)): sweepUp.Mode = 6: sweepUp.SetRadius 1, 1.0: geomSet.AppendHybridShape sweepUp

    Dim lineDown, ribbonDown, curveDown, sweepDown
    Set lineDown = hsf.AddNewLinePtDir(ref1, dirDown, 0.0, 50.0, False): geomSet.AppendHybridShape lineDown
    Set ribbonDown = hsf.AddNewSweepExplicit(part1.CreateReferenceFromObject(lineDown), splineRef): geomSet.AppendHybridShape ribbonDown
    Set curveDown = hsf.AddNewIntersection(part1.CreateReferenceFromObject(ribbonDown), sweepRef): curveDown.Name = "Wire_Path_Down": geomSet.AppendHybridShape curveDown
    Set sweepDown = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(curveDown)): sweepDown.Mode = 6: sweepDown.SetRadius 1, 1.0: geomSet.AppendHybridShape sweepDown

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
    currentDist = 20.0
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
        ribSweep.SetRadius 1, 1.5
        ribSweep.Name = "Circular_Rib_Sweep_" & CStr(ribCounter)
        ribsSet.AppendHybridShape ribSweep

        currentDist = currentDist + 20.0
        ribCounter = ribCounter + 1
    Loop

    part1.Update()

    ' --- Solidification ---
    Dim shapeFactory
    Set shapeFactory = part1.ShapeFactory
    
    ' 1. Hollow Main Tube
    part1.InWorkObject = part1.MainBody
    Dim thickMain
    Set thickMain = shapeFactory.AddNewThickSurface(sweepRef, 1, 2.5, 0.0)
    
    ' 2. Vertical Ribs Solid Body
    Dim body1
    Set body1 = part1.Bodies.Add()
    body1.Name = "Body.1_Vertical_Ribs"
    part1.InWorkObject = body1
    
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepRight))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepLeft))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepUp))
    shapeFactory.AddNewCloseSurface(part1.CreateReferenceFromObject(sweepDown))
    
    ' 3. Circular Ribs Solid Body
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

    ' Force update before Boolean Operations
    part1.Update()

    ' --- Boolean ADD (More robust than Assemble) ---
    part1.InWorkObject = part1.MainBody
    
    ' Add Vertical Ribs into MainBody
    Dim addVert
    Set addVert = shapeFactory.AddNewAdd(body1)
    part1.UpdateObject addVert ' Update sequentially
    
    ' Add Circular Ribs into MainBody
    Dim addCirc
    Set addCirc = shapeFactory.AddNewAdd(body2)
    part1.UpdateObject addCirc ' Update sequentially

    part1.Update()
End Sub
