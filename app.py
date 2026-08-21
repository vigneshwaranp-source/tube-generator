Sub CATMain()
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

    Dim pt1: Set pt1 = hsf.AddNewPointCoord(0.0, 0.0, 0.0): pt1.Name = "30": geomSet.AppendHybridShape pt1
    Dim ref1: Set ref1 = part1.CreateReferenceFromObject(pt1): spline.AddPoint ref1

    Dim pt2: Set pt2 = hsf.AddNewPointCoord(150.0, 150.0, 150.0): pt2.Name = "31": geomSet.AppendHybridShape pt2
    Dim ref2: Set ref2 = part1.CreateReferenceFromObject(pt2): spline.AddPoint ref2

    Dim pt3: Set pt3 = hsf.AddNewPointCoord(300.0, -50.0, 300.0): pt3.Name = "32": geomSet.AppendHybridShape pt3
    Dim ref3: Set ref3 = part1.CreateReferenceFromObject(pt3): spline.AddPoint ref3

    Dim pt4: Set pt4 = hsf.AddNewPointCoord(150.0, -250.0, 450.0): pt4.Name = "33": geomSet.AppendHybridShape pt4
    Dim ref4: Set ref4 = part1.CreateReferenceFromObject(pt4): spline.AddPoint ref4

    Dim pt5: Set pt5 = hsf.AddNewPointCoord(-100.0, -100.0, 600.0): pt5.Name = "34": geomSet.AppendHybridShape pt5
    Dim ref5: Set ref5 = part1.CreateReferenceFromObject(pt5): spline.AddPoint ref5

    Dim pt6: Set pt6 = hsf.AddNewPointCoord(-200.0, 150.0, 750.0): pt6.Name = "35": geomSet.AppendHybridShape pt6
    Dim ref6: Set ref6 = part1.CreateReferenceFromObject(pt6): spline.AddPoint ref6

    Dim pt7: Set pt7 = hsf.AddNewPointCoord(0.0, 300.0, 900.0): pt7.Name = "36": geomSet.AppendHybridShape pt7
    Dim ref7: Set ref7 = part1.CreateReferenceFromObject(pt7): spline.AddPoint ref7

    geomSet.AppendHybridShape spline
    Dim splineRef: Set splineRef = part1.CreateReferenceFromObject(spline)

    ' ==========================================
    ' PLANES, CIRCLES & CLOSING POINTS
    ' ==========================================
    Dim dirY: Set dirY = hsf.AddNewDirectionByCoord(0, 1, 0)

    Dim plane1: Set plane1 = hsf.AddNewPlaneNormal(splineRef, ref1): geomSet.AppendHybridShape plane1
    Dim refPlane1: Set refPlane1 = part1.CreateReferenceFromObject(plane1)
    Dim circle1: Set circle1 = hsf.AddNewCircleCtrRad(ref1, refPlane1, True, 25.0): geomSet.AppendHybridShape circle1
    Dim refCircle1: Set refCircle1 = part1.CreateReferenceFromObject(circle1)
    Dim closePt1: Set closePt1 = hsf.AddNewExtremum(refCircle1, dirY, 1): geomSet.AppendHybridShape closePt1
    Dim refClosePt1: Set refClosePt1 = part1.CreateReferenceFromObject(closePt1)

    Dim plane2: Set plane2 = hsf.AddNewPlaneNormal(splineRef, ref2): geomSet.AppendHybridShape plane2
    Dim refPlane2: Set refPlane2 = part1.CreateReferenceFromObject(plane2)
    Dim circle2: Set circle2 = hsf.AddNewCircleCtrRad(ref2, refPlane2, True, 50.0): geomSet.AppendHybridShape circle2
    Dim refCircle2: Set refCircle2 = part1.CreateReferenceFromObject(circle2)
    Dim closePt2: Set closePt2 = hsf.AddNewExtremum(refCircle2, dirY, 1): geomSet.AppendHybridShape closePt2
    Dim refClosePt2: Set refClosePt2 = part1.CreateReferenceFromObject(closePt2)

    Dim plane3: Set plane3 = hsf.AddNewPlaneNormal(splineRef, ref3): geomSet.AppendHybridShape plane3
    Dim refPlane3: Set refPlane3 = part1.CreateReferenceFromObject(plane3)
    Dim circle3: Set circle3 = hsf.AddNewCircleCtrRad(ref3, refPlane3, True, 20.0): geomSet.AppendHybridShape circle3
    Dim refCircle3: Set refCircle3 = part1.CreateReferenceFromObject(circle3)
    Dim closePt3: Set closePt3 = hsf.AddNewExtremum(refCircle3, dirY, 1): geomSet.AppendHybridShape closePt3
    Dim refClosePt3: Set refClosePt3 = part1.CreateReferenceFromObject(closePt3)

    Dim plane4: Set plane4 = hsf.AddNewPlaneNormal(splineRef, ref4): geomSet.AppendHybridShape plane4
    Dim refPlane4: Set refPlane4 = part1.CreateReferenceFromObject(plane4)
    Dim circle4: Set circle4 = hsf.AddNewCircleCtrRad(ref4, refPlane4, True, 60.0): geomSet.AppendHybridShape circle4
    Dim refCircle4: Set refCircle4 = part1.CreateReferenceFromObject(circle4)
    Dim closePt4: Set closePt4 = hsf.AddNewExtremum(refCircle4, dirY, 1): geomSet.AppendHybridShape closePt4
    Dim refClosePt4: Set refClosePt4 = part1.CreateReferenceFromObject(closePt4)

    Dim plane5: Set plane5 = hsf.AddNewPlaneNormal(splineRef, ref5): geomSet.AppendHybridShape plane5
    Dim refPlane5: Set refPlane5 = part1.CreateReferenceFromObject(plane5)
    Dim circle5: Set circle5 = hsf.AddNewCircleCtrRad(ref5, refPlane5, True, 30.0): geomSet.AppendHybridShape circle5
    Dim refCircle5: Set refCircle5 = part1.CreateReferenceFromObject(circle5)
    Dim closePt5: Set closePt5 = hsf.AddNewExtremum(refCircle5, dirY, 1): geomSet.AppendHybridShape closePt5
    Dim refClosePt5: Set refClosePt5 = part1.CreateReferenceFromObject(closePt5)

    Dim plane6: Set plane6 = hsf.AddNewPlaneNormal(splineRef, ref6): geomSet.AppendHybridShape plane6
    Dim refPlane6: Set refPlane6 = part1.CreateReferenceFromObject(plane6)
    Dim circle6: Set circle6 = hsf.AddNewCircleCtrRad(ref6, refPlane6, True, 55.0): geomSet.AppendHybridShape circle6
    Dim refCircle6: Set refCircle6 = part1.CreateReferenceFromObject(circle6)
    Dim closePt6: Set closePt6 = hsf.AddNewExtremum(refCircle6, dirY, 1): geomSet.AppendHybridShape closePt6
    Dim refClosePt6: Set refClosePt6 = part1.CreateReferenceFromObject(closePt6)

    Dim plane7: Set plane7 = hsf.AddNewPlaneNormal(splineRef, ref7): geomSet.AppendHybridShape plane7
    Dim refPlane7: Set refPlane7 = part1.CreateReferenceFromObject(plane7)
    Dim circle7: Set circle7 = hsf.AddNewCircleCtrRad(ref7, refPlane7, True, 25.0): geomSet.AppendHybridShape circle7
    Dim refCircle7: Set refCircle7 = part1.CreateReferenceFromObject(circle7)
    Dim closePt7: Set closePt7 = hsf.AddNewExtremum(refCircle7, dirY, 1): geomSet.AppendHybridShape closePt7
    Dim refClosePt7: Set refClosePt7 = part1.CreateReferenceFromObject(closePt7)

    ' ==========================================
    ' MAIN TUBE LOFT (Freeflow)
    ' ==========================================
    Dim mainLoft: Set mainLoft = hsf.AddNewLoft()
    mainLoft.SectionCoupling = 1
    mainLoft.AddSectionToLoft refCircle1, 1, refClosePt1
    mainLoft.AddSectionToLoft refCircle2, 1, refClosePt2
    mainLoft.AddSectionToLoft refCircle3, 1, refClosePt3
    mainLoft.AddSectionToLoft refCircle4, 1, refClosePt4
    mainLoft.AddSectionToLoft refCircle5, 1, refClosePt5
    mainLoft.AddSectionToLoft refCircle6, 1, refClosePt6
    mainLoft.AddSectionToLoft refCircle7, 1, refClosePt7

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

    ' FIX: Set Vertical Ribs to 1.9mm Radius (3.8mm Dia) to prevent zero-thickness Boolean clash
    Dim sweepU: Set sweepU = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(crvU)): sweepU.Mode = 6: sweepU.SetRadius 1, 1.9: sweepU.Name = "Sweep_Top": linesSet.AppendHybridShape sweepU
    Dim sweepD: Set sweepD = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(crvD)): sweepD.Mode = 6: sweepD.SetRadius 1, 1.9: sweepD.Name = "Sweep_Bottom": linesSet.AppendHybridShape sweepD
    Dim sweepR: Set sweepR = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(crvR)): sweepR.Mode = 6: sweepR.SetRadius 1, 1.9: sweepR.Name = "Sweep_Right": linesSet.AppendHybridShape sweepR
    Dim sweepL: Set sweepL = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(crvL)): sweepL.Mode = 6: sweepL.SetRadius 1, 1.9: sweepL.Name = "Sweep_Left": linesSet.AppendHybridShape sweepL

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
    targetSpacing = 30.0 
    
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
        
        ' FIX: Set Circular Ribs to 2.0mm Radius (4mm Dia). By being 0.1mm larger than the vertical ribs, the Boolean engine computes the split cleanly!
        Dim circSweep
        Set circSweep = hsf.AddNewSweepCircle(part1.CreateReferenceFromObject(nearIntersect))
        circSweep.Mode = 6
        circSweep.SetRadius 1, 2.0
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
    Set thickMain = shapeFactory.AddNewThickSurface(sweepRef, 1, 3.5, 0.0)
    
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
