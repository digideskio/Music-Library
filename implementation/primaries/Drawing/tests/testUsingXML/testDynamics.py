import os

from implementation.primaries.Drawing.tests.testUsingXML.setup import xmlSet, parsePiece
from implementation.primaries.Drawing.classes.ObjectHierarchy.ItemClasses import Directions
from implementation.primaries.Drawing.classes.ObjectHierarchy.TreeClasses.MeasureNode import MeasureNode
from implementation.primaries.Drawing.classes.ObjectHierarchy.TreeClasses.NoteNode import NoteNode
from implementation.primaries.Drawing.classes.ObjectHierarchy.TreeClasses.PartNode import PartNode
from implementation.primaries.Drawing.classes.ObjectHierarchy.TreeClasses.BaseTree import Search
from implementation.primaries.Drawing.classes.ObjectHierarchy.TreeClasses.OtherNodes import ExpressionNode


partname = "dynamics.xml"
folder = "/Users/charlottegodley/PycharmProjects/FYP/implementation/primaries/SampleMusicXML/testcases"


class testFile(xmlSet):
    def setUp(self):
        xmlSet.setUp(self)
        self.m_num = 32
        self.p_id = "P1"
        self.p_name = "Flute"
        self.piece = parsePiece(os.path.join(folder, partname))

    def testParts(self):
        global piece
        self.assertIsInstance(self.piece.getPart(self.p_id), PartNode)
        self.assertEqual(self.p_name, self.piece.getPart(self.p_id).GetItem().name)

    def testMeasures(self):
        self.assertIsInstance(self.piece.getPart(self.p_id).getMeasure(self.m_num, 1), MeasureNode)

class testDynamics(xmlSet):
    def setUp(self):
        xmlSet.setUp(self)
        self.m_num = 32
        self.p_id = "P1"
        self.p_name = "Flute"
        self.piece = parsePiece(os.path.join(folder, partname))

    def tearDown(self):
        self.piece = None

    def testMeasure1Direction1(self):
        measure = self.piece.getPart(self.p_id).getMeasure(1,1)
        note = Search(NoteNode, measure, 1)
        exp =  Search(ExpressionNode, note, 1)

        self.assertIsInstance(exp.GetItem(), Directions.Dynamic)

    def testMeasure1Direction1Val(self):
        measure = self.piece.getPart(self.p_id).getMeasure(1,1)
        note = Search(NoteNode, measure, 1)
        exp =  Search(ExpressionNode, note, 1)

        self.assertEqual("ppp", exp.GetItem().mark)

    def testMeasure1Direction3(self):
        measure = self.piece.getPart(self.p_id).getMeasure(1,1)
        note = Search(NoteNode, measure, 2)
        exp =  Search(ExpressionNode, note, 1)
        self.assertIsInstance(exp.GetItem(), Directions.Dynamic)

    def testMeasure1Direction3Val(self):
        measure = self.piece.getPart(self.p_id).getMeasure(1,1)
        note = Search(NoteNode, measure, 2)
        exp =  Search(ExpressionNode, note, 1)
        self.assertEqual("pp", exp.GetItem().mark)

    def testMeasure1Direction5(self):
        measure = self.piece.getPart(self.p_id).getMeasure(1,1)
        note = Search(NoteNode, measure, 2)
        exp =  Search(ExpressionNode, note, 1)
        self.assertIsInstance(exp.GetItem(), Directions.Dynamic)

    def testMeasure1Direction5Val(self):
        measure = self.piece.getPart(self.p_id).getMeasure(1,1)
        note = Search(NoteNode, measure, 3)
        exp =  Search(ExpressionNode, note, 1)
        self.assertEqual("p", exp.GetItem().mark)

    def testMeasure1Direction7(self):
        measure = self.piece.getPart(self.p_id).getMeasure(1,1)
        note = Search(NoteNode, measure, 4)
        exp =  Search(ExpressionNode, note, 1)
        self.assertIsInstance(exp.GetItem(), Directions.Dynamic)

    def testMeasure1Direction7Val(self):
        measure = self.piece.getPart(self.p_id).getMeasure(1,1)
        note = Search(NoteNode, measure, 4)
        exp = Search(ExpressionNode, note, 1)
        self.assertEqual("mp", exp.GetItem().mark)

    def testMeasure2Direction1(self):
        measure = self.piece.getPart(self.p_id).getMeasure(2,1)
        note = Search(NoteNode, measure, 1)
        exp = Search(ExpressionNode, note, 1)
        self.assertIsInstance(exp.GetItem(), Directions.Dynamic)

    def testMeasure2Direction1Val(self):
        measure = self.piece.getPart(self.p_id).getMeasure(2,1)
        note = Search(NoteNode, measure, 1)
        exp = Search(ExpressionNode, note, 1)
        self.assertEqual("mf", exp.GetItem().mark)

    def testMeasure2Direction4(self):
        measure = self.piece.getPart(self.p_id).getMeasure(2,1)
        note = Search(NoteNode, measure, 3)
        exp = Search(ExpressionNode, note, 1)
        self.assertIsInstance(exp.GetItem(), Directions.Dynamic)

    def testMeasure2Direction4Val(self):
        measure = self.piece.getPart(self.p_id).getMeasure(2,1)
        note = Search(NoteNode, measure, 3)
        exp = Search(ExpressionNode, note, 1)
        self.assertEqual("f", Search(ExpressionNode, note, 1).GetItem().mark)

    def testMeasure3Direction1(self):
        measure = self.piece.getPart(self.p_id).getMeasure(3,1)
        note = Search(NoteNode, measure, 1)
        self.assertIsInstance(Search(ExpressionNode, note, 1).GetItem(), Directions.Dynamic)

    def testMeasure3Direction1Val(self):
        measure = self.piece.getPart(self.p_id).getMeasure(3,1)
        note = Search(NoteNode, measure, 1)
        exp = Search(ExpressionNode, note, 1)
        self.assertEqual("ff", exp.GetItem().mark)

    def testMeasure3Direction5(self):
        measure = self.piece.getPart(self.p_id).getMeasure(3,1)
        note = Search(NoteNode, measure, 4)
        exp = Search(ExpressionNode, note, 1)
        self.assertIsInstance(exp.GetItem(), Directions.Dynamic)

    def testMeasure3Direction5Val(self):
        measure = self.piece.getPart(self.p_id).getMeasure(3,1)
        note = Search(NoteNode, measure, 4)
        exp = Search(ExpressionNode, note, 1)
        self.assertEqual("fff", exp.GetItem().mark)
