import unittest
from implementation.primaries.Drawing.classes.tree_cls import BaseTree,PieceTree

class testPieceTree(unittest.TestCase):
    def setUp(self):
        self.item = PieceTree.PieceTree()

    def testAddPartGroup(self):
        part = PieceTree.PartNode()
        part2 = PieceTree.PartNode()
        self.item.AddNode(part, index="P1")
        self.item.AddNode(part2, index="P2")
        self.item.AddToGroup("wind", index="P1")
        self.item.AddToGroup("wind", index="P2")
        self.assertEqual(self.item.getGroup("wind"), ["P1","P2"])

    def testAddPart(self):
        part = PieceTree.PartNode()
        self.item.AddNode(part, index="P1")
        self.assertEqual(self.item.FindNodeByIndex("P1"), part)

    def testAddInvalidMeasure(self):
        measure = PieceTree.MeasureNode()
        with self.assertRaises(BaseTree.CannotAddToTreeException):
            self.item.AddNode(measure, index=1)

    def testFindStaff(self):
        part = PieceTree.PartNode()
        staff = PieceTree.StaffNode()
        self.item.AddNode(part, index="P1")
        self.item.AddNode(staff, index=1)
        self.assertEqual(part.getStaff(1), staff)

    def testFindMeasure(self):
        part = PieceTree.PartNode()
        staff = PieceTree.StaffNode()
        self.item.AddNode(part, index="P1")
        self.item.AddNode(staff, index=1)
        measure = PieceTree.MeasureNode()
        self.item.AddNode(measure, index=1)
        self.assertEqual(part.getMeasure(1, 1), measure)

    def testAddMeasureOnSecondStave(self):
        part = PieceTree.PartNode()
        staff = PieceTree.StaffNode()
        staff2 = PieceTree.StaffNode()
        measure = None
        self.item.AddNode(part, index="P1")
        self.item.AddNode(staff, index=1)
        self.item.AddNode(staff2, index=2)
        part.addMeasure(measure,staff=2)
        self.assertEqual(part.getMeasure(1,2).GetItem(),measure)

class testAddToMeasure(unittest.TestCase):
    def setUp(self):
        self.item = PieceTree.PieceTree()
        self.part = PieceTree.PartNode()
        self.item.AddNode(self.part, index="P1")
        self.part.addEmptyMeasure()
        self.measure = self.part.getMeasure()

    def testAddNote(self):
        note = "3"
        self.measure.addNote(note)
        voice = self.measure.getVoice(1)
        self.assertEqual(voice.GetChild(0).GetItem(), note)

    def testAddDirection(self):
        direction = "2"
        self.measure.addDirection(direction)
        voice = self.measure.getVoice(1)
        self.assertEqual(voice.GetChild(0).GetChild(0).GetItem(), direction)

    def testAddExpression(self):
        exp = "2"
        self.measure.addExpression(exp)
        voice = self.measure.getVoice(1)
        self.assertEqual(voice.GetChild(0).GetChild(0).GetItem(), exp)

    def testAddPlaceholder(self):
        self.measure.addPlaceholder()
        voice = self.measure.getVoice(1)
        self.assertEqual(voice.GetChild(0).GetItem(), None)

    def testAddNoteWithPlaceholderBeforeIt(self):
        note=2
        self.measure.addNote(note)
        self.measure.index = 0
        self.measure.addPlaceholder()
        voice = self.measure.getVoice(1)
        self.assertEqual(voice.GetChild(0).GetItem(), None)

    def testForward(self):
        self.measure.addNote(1)
        self.measure.Forward(duration=16)
        self.assertEqual(self.measure.index, 2)

    def testBackup(self):
        self.measure.addNote(1)
        self.measure.Backup(duration=15)
        self.assertEqual(self.measure.index, 0)

    def testForwardCreatesAPlaceholder(self):
        self.measure.addNote(1)
        self.measure.Forward(duration=16)
        voice = self.measure.getVoice(1)
        self.assertIsInstance(voice.GetChild(1), PieceTree.NoteNode)

    def testBackupAndAddNote(self):
        self.measure.addNote(1)
        self.measure.Backup(duration=15)
        self.measure.addNote(2)
        voice = self.measure.getVoice(1)
        self.assertEqual(voice.GetChild(0).GetItem(), 2)

    def testAddDirectionThenNode(self):
        dir = 1
        note = 3
        self.measure.addDirection(dir)
        self.measure.addNote(note)
        voice = self.measure.getVoice(1)
        self.assertEqual(voice.GetChild(0).GetItem(), note)

    def testAddDirectionToSecondNote(self):
        dir = 1
        note = 2
        note1 = 3
        self.measure.addNote(note)
        self.measure.addNote(note1)
        self.measure.addDirection(dir)
        voice = self.measure.getVoice(1)
        self.assertEqual(voice.GetChild(1).GetChild(0).GetItem(), dir)

    def testAddChordNote(self):
        note = 2
        note1 = 3
        self.measure.addNote(note)
        self.measure.addNote(note1, chord=True)
        voice = self.measure.getVoice(1)
        self.assertEqual(voice.GetChild(0).GetChild(0).GetItem(), 3)

    def testAddExpressionThenChordNote(self):
        note = 2
        note1 = 3
        exp = 0
        self.measure.addNote(note)
        self.measure.addExpression(exp)
        self.measure.addNote(note1, chord=True)
        voice = self.measure.getVoice(1)
        self.assertEqual(voice.GetChild(0).GetChild(0).GetItem(), 3)