from implementation.primaries.Drawing.tests.testUsingXML.setup import xmlSet, parsePiece
from implementation.primaries.Drawing.classes import Note
from implementation.primaries.Drawing.classes.tree_cls.PieceTree import MeasureNode, NoteNode, Search
import os

partname = "beams.xml"
folder = "/Users/charlottegodley/PycharmProjects/FYP/implementation/primaries/SampleMusicXML/testcases"
piece = parsePiece(os.path.join(folder, partname))

class testArpeg(xmlSet):
    def setUp(self):
        xmlSet.setUp(self)
        self.m_num = 32
        self.p_id = "P1"
        self.p_name = "Flute"

    def testParts(self):
        global piece
        self.assertTrue(self.p_id in piece.root.GetChildrenIndexes())
        self.assertEqual(self.p_name, piece.getPart(self.p_id).GetItem().name)

    def testMeasures(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=self.m_num, staff=1)
        self.assertIsInstance(measure, MeasureNode)


    def testNote2ID(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 2).GetItem()
        self.assertTrue(1 in item.beams)

    def testNote2Type(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 2).GetItem()
        self.assertEqual("begin", item.beams[1].type)

    def testNote3(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 3).GetItem()
        self.assertTrue(hasattr(item, "beams"))

    def testNote3ID(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 3).GetItem()
        self.assertTrue(1 in item.beams)

    def testNote3Type(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 3).GetItem()
        self.assertEqual("continue", item.beams[1].type)

    def testNote4(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 4).GetItem()
        self.assertTrue(hasattr(item, "beams"))

    def testNote4ID(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 4).GetItem()
        self.assertTrue(1 in item.beams)

    def testNote4Type(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 4).GetItem()
        self.assertEqual("end", item.beams[1].type)


    def testNote6(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 6).GetItem()
        self.assertTrue(hasattr(item, "beams"))

    def testNote6ID(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 6).GetItem()
        self.assertTrue(1 in item.beams)

    def testNote6Type(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 6).GetItem()
        self.assertEqual("begin", item.beams[1].type)

    def testNote7(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 7).GetItem()
        self.assertTrue(hasattr(item, "beams"))

    def testNote7ID(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 7).GetItem()
        self.assertTrue(1 in item.beams)

    def testNote7Type(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 7).GetItem()
        self.assertEqual("continue", item.beams[1].type)

    def testNote8(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 8).GetItem()
        self.assertTrue(hasattr(item, "beams"))

    def testNote8ID(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 8).GetItem()
        self.assertTrue(1 in item.beams)

    def testNote8Type(self):
        part = piece.getPart(self.p_id)
        measure = part.getMeasure(measure=1, staff=1)
        item = Search(NoteNode, measure, 8).GetItem()
        self.assertEqual("end", item.beams[1].type)


