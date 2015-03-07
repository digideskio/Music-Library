from implementation.primaries.Drawing.tests.testLilyMethods.setup import Lily
from implementation.primaries.Drawing.tests.testLilyMethods.testMeasure import MeasureTests
from implementation.primaries.Drawing.classes import Measure, Note
from implementation.primaries.Drawing.classes.tree_cls.PieceTree import MeasureNode, StaffNode
import unittest

class testNormalBarline(Lily):
    def setUp(self):
        self.item = Measure.Barline(style="normal")
        self.lilystring = " \\bar \"|\""

class testDottedBarline(Lily):
    def setUp(self):
        self.item = Measure.Barline(style="dotted")
        self.lilystring = " \\bar \";\""

class testDashedBarline(Lily):
    def setUp(self):
        self.item = Measure.Barline(style="dashed")
        self.lilystring = " \\bar \"!\""

class testHeavyLightBarline(Lily):
    def setUp(self):
        self.item = Measure.Barline(style="heavy-light")
        self.lilystring = " \\bar \".|\""

class testLightHeavyBarline(Lily):
    def setUp(self):
        self.item = Measure.Barline(style="light-heavy")
        self.lilystring = " \\bar \"|.\""

class testLightLightBarline(Lily):
    def setUp(self):
        self.item = Measure.Barline(style="light-light")
        self.lilystring = " \\bar \"||\""

class testHeavyHeavyBarline(Lily):
    def setUp(self):
        self.item = Measure.Barline(style="heavy-heavy")
        self.lilystring = " \\bar \"..\""

class testForwardRepeat(Lily):
    def setUp(self):
        self.item = Measure.Barline(style="heavy-light", repeat="forward")
        self.lilystring = " \\repeat volta 2 {"

class testBackwardRepeat(Lily):
    def setUp(self):
        self.item = Measure.Barline(style="light-heavy", repeat="backward")
        self.lilystring = "}"

class testEndingMark(Lily):
    def setUp(self):
        self.item = Measure.EndingMark()
        self.lilystring = "\\alternative {{"

class testEndingMark2(Lily):
    def setUp(self):
        self.item = Measure.EndingMark(number=2)
        self.lilystring = "{"

class testEndingMarkEnd(Lily):
    def setUp(self):
        self.item = Measure.EndingMark(type="stop")
        self.lilystring = "}"

class testEndingMarkEndOfAll(Lily):
    def setUp(self):
        self.item = Measure.EndingMark(type="discontinue")
        self.lilystring = "}\n}"

class testBarlineWithEndingStart(Lily):
    def setUp(self):
        self.item = Measure.Barline(style="heavy-light",ending=Measure.EndingMark())
        self.lilystring = "\\alternative {{"

class testMeasureLeftBarline(MeasureTests):
    def setUp(self):
        self.item = MeasureNode()
        note = Note.Note()
        note.pitch = Note.Pitch()
        self.item.addNote(note)
        self.item.AddBarline(Measure.Barline(repeat="forward"),location="left")
        self.lilystring = " \\repeat volta 2 {c'  | "

class testMeasureRightBarline(MeasureTests):
    def setUp(self):
        self.item = MeasureNode()
        note = Note.Note()
        note.pitch = Note.Pitch()
        self.item.addNote(note)
        self.item.AddBarline(Measure.Barline(repeat="forward"), location="left")
        self.item.AddBarline(Measure.Barline(repeat="backward"), location="right")
        self.lilystring = " \\repeat volta 2 {c' }"


class testMeasureRightRepeatBarlineNoLeft(MeasureTests):
    def setUp(self):
        self.item = MeasureNode()
        note = Note.Note()
        note.pitch = Note.Pitch()
        self.item.addNote(note)
        self.item.AddBarline(Measure.Barline(repeat="backward-barline"), location="right")
        self.lilystring = "c'  \\bar \":|.\""

class testStaffMeasureFlagValues(unittest.TestCase):
    def setUp(self):
        self.item = StaffNode()
        self.item.AddBarline(item=Measure.Barline(repeat="forward"), location="left", measure_id=1)


    def testFlagExists(self):
        self.assertTrue(hasattr(self.item, "forward_repeats"))

    def testFlagValue(self):
        self.assertEqual(len(self.item.forward_repeats), 1)

    def testBackwardFlag(self):
        self.item.AddBarline(item=Measure.Barline(repeat="backward"), location="right", measure_id=1)
        self.assertTrue(hasattr(self.item, "forward_repeats"))

    def testBackwardFlagValue(self):
        self.item.AddBarline(item=Measure.Barline(repeat="backward"), location="right", measure_id=1)
        self.assertEqual(len(self.item.backward_repeats), 0)

    def testFOrwardFlagValueAfterBackwardAdded(self):
        self.item.AddBarline(item=Measure.Barline(repeat="backward"), location="right", measure_id=1)
        self.assertEqual(len(self.item.forward_repeats), 0)