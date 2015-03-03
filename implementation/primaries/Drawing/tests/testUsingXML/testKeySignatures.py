from implementation.primaries.Drawing.tests.testUsingXML.setup import xmlSet, parsePiece
from implementation.primaries.Drawing.classes import Key
from implementation.primaries.Drawing.classes.tree_cls.PieceTree import PartNode, MeasureNode, KeyNode
import os

partname = "keySignatures.xml"
folder = "/Users/charlottegodley/PycharmProjects/FYP/implementation/primaries/SampleMusicXML/testcases"
piece = parsePiece(os.path.join(folder, partname))

class testFile(xmlSet):
    def setUp(self):
        xmlSet.setUp(self)
        self.m_num = 15
        self.p_id = "P1"
        self.p_name = "Flute"

    def testParts(self):
        global piece
        self.assertIsInstance(piece.getPart(self.p_id), PartNode)
        self.assertEqual(self.p_name, piece.getPart(self.p_id).GetItem().name)

    def testMeasures(self):
        self.assertIsInstance(piece.getPart(self.p_id).getMeasure(1,1), MeasureNode)

class testKeySig(xmlSet):
    def setUp(self):
        xmlSet.setUp(self)
        self.p_id = "P1"
        if hasattr(self, "measure_id"):
            self.measure = piece.getPart(self.p_id).getMeasure(self.measure_id, 1)
    def testHasKey(self):
        if hasattr(self, "measure"):
            self.assertIsInstance(self.measure.GetLastKey(), KeyNode)


    def testKeyFifths(self):
        if hasattr(self, "measure"):
            self.assertEqual(self.fifths, self.measure.GetLastKey().GetItem().fifths)

    def testKeyMode(self):
        if hasattr(self, "measure"):
            self.assertEqual(self.mode, self.measure.GetLastKey().GetItem().mode)

class testMeasure1(testKeySig):
    def setUp(self):
        self.measure_id = 1
        self.fifths = "1"
        self.mode = "major"
        testKeySig.setUp(self)

class testMeasure2(testKeySig):
    def setUp(self):
        self.measure_id = 2
        self.fifths = "2"
        self.mode = "major"
        testKeySig.setUp(self)

class testMeasure3(testKeySig):
    def setUp(self):
        self.measure_id = 3
        self.fifths = "3"
        self.mode = "major"
        testKeySig.setUp(self)

class testMeasure4(testKeySig):
    def setUp(self):
        self.measure_id = 4
        self.fifths = "4"
        self.mode = "major"
        testKeySig.setUp(self)

class testMeasure5(testKeySig):
    def setUp(self):
        self.measure_id = 5
        self.fifths = "5"
        self.mode = "major"
        testKeySig.setUp(self)

class testMeasure6(testKeySig):
    def setUp(self):
        self.measure_id = 6
        self.fifths = "6"
        self.mode = "major"
        testKeySig.setUp(self)

class testMeasure7(testKeySig):
    def setUp(self):
        self.measure_id = 7
        self.fifths = "7"
        self.mode = "major"
        testKeySig.setUp(self)

class testMeasure8(testKeySig):
    def setUp(self):
        self.measure_id = 8
        self.fifths = "-7"
        self.mode = "major"
        testKeySig.setUp(self)

class testMeasure9(testKeySig):
    def setUp(self):
        self.measure_id = 9
        self.fifths = "-6"
        self.mode = "major"
        testKeySig.setUp(self)

class testMeasure10(testKeySig):
    def setUp(self):
        self.measure_id = 10
        self.fifths = "-5"
        self.mode = "major"
        testKeySig.setUp(self)

class testMeasure11(testKeySig):
    def setUp(self):
        self.measure_id = 11
        self.fifths = "-4"
        self.mode = "major"
        testKeySig.setUp(self)

class testMeasure12(testKeySig):
    def setUp(self):
        self.measure_id = 12
        self.fifths = "-3"
        self.mode = "major"
        testKeySig.setUp(self)

class testMeasure13(testKeySig):
    def setUp(self):
        self.measure_id = 13
        self.fifths = "-2"
        self.mode = "major"
        testKeySig.setUp(self)

class testMeasure14(testKeySig):
    def setUp(self):
        self.measure_id = 14
        self.fifths = "-1"
        self.mode = "major"
        testKeySig.setUp(self)

class testMeasure15(testKeySig):
    def setUp(self):
        self.measure_id = 15
        self.fifths = "0"
        self.mode = "major"
        testKeySig.setUp(self)
