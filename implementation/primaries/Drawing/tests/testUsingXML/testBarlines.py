from implementation.primaries.Drawing.tests.testUsingXML.setup import xmlSet, parsePiece
from implementation.primaries.Drawing.classes import Measure
from implementation.primaries.Drawing.classes.tree_cls.PieceTree import MeasureNode
import os

partname = "barlines.xml"
folder = "/Users/charlottegodley/PycharmProjects/FYP/implementation/primaries/SampleMusicXML/testcases"
piece = parsePiece(os.path.join(folder, partname))

class testBarlines(xmlSet):
    def setUp(self):
        xmlSet.setUp(self)
        self.m_num = 32
        self.p_id = "P1"
        self.p_name = "Piano"

    def testParts(self):
        global piece
        self.assertTrue(self.p_id in piece.root.GetChildrenIndexes())
        self.assertEqual(self.p_name, piece.getPart(self.p_id).GetItem().name)

    def testMeasures(self):
        self.assertIsInstance(piece.getPart(self.p_id).getMeasure(measure=1,staff=1), MeasureNode)

    def testMeasure2Barline(self):
        part=piece.getPart(self.p_id)
        item=part.getMeasure(measure=2,staff=1).GetItem()
        self.assertTrue(hasattr(item, "barlines"))

    def testMeasure2BarlineLocation(self):
        part=piece.getPart(self.p_id)
        item=part.getMeasure(measure=2,staff=1).GetItem()
        self.assertTrue("right" in item.barlines)

    def testMeasure2BarlineInstance(self):
        part=piece.getPart(self.p_id)
        item=part.getMeasure(measure=2,staff=1).GetItem()
        self.assertIsInstance(item.barlines["right"], Measure.Barline)

    def testMeasure2BarlineStyle(self):
        part=piece.getPart(self.p_id)
        item=part.getMeasure(measure=2,staff=1).GetItem()
        self.assertEqual("dashed", item.barlines["right"].style)

    def testMeasure4Barline(self):
        part=piece.getPart(self.p_id)
        item=part.getMeasure(measure=4,staff=1).GetItem()
        self.assertTrue(hasattr(item, "barlines"))

    def testMeasure4BarlineInstance(self):
        part=piece.getPart(self.p_id)
        item=part.getMeasure(measure=4,staff=1).GetItem()
        self.assertIsInstance(item.barlines["right"], Measure.Barline)

    def testMeasure4BarlineRight(self):
        part=piece.getPart(self.p_id)
        item=part.getMeasure(measure=4,staff=1).GetItem()
        self.assertTrue("right" in item.barlines)

    def testMeasure4BarlineRightStyle(self):
        part=piece.getPart(self.p_id)
        item=part.getMeasure(measure=4,staff=1).GetItem()
        self.assertEqual("light-heavy", item.barlines["right"].style)

    def testMeasure5Barline(self):
        part=piece.getPart(self.p_id)
        item=part.getMeasure(measure=5,staff=1).GetItem()
        self.assertTrue(hasattr(item, "barlines"))

    def testMeasure5BarlineRight(self):
        part=piece.getPart(self.p_id)
        item=part.getMeasure(measure=5,staff=1).GetItem()
        self.assertTrue("right" in item.barlines)

    def testMeasure5BarlineRightInstance(self):
        part=piece.getPart(self.p_id)
        item=part.getMeasure(measure=5,staff=1).GetItem()
        self.assertIsInstance(item.barlines["right"], Measure.Barline)

    def testMeasure5BarlineStyle(self):
        part=piece.getPart(self.p_id)
        item=part.getMeasure(measure=5,staff=1).GetItem()
        self.assertEqual("light-light", item.barlines["right"].style)