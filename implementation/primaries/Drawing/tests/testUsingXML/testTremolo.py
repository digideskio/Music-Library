from implementation.primaries.Drawing.tests.testUsingXML.setup import xmlSet, parsePiece
from implementation.primaries.Drawing.classes import Ornaments
import os

partname = "tremolo.xml"
folder = "/Users/charlottegodley/PycharmProjects/FYP/implementation/primaries/SampleMusicXML/testcases"
piece = parsePiece(os.path.join(folder, partname))

class testFile(xmlSet):
    def setUp(self):
        xmlSet.setUp(self)
        self.m_num = 32
        self.p_id = "P1"
        self.p_name = "Flute"

    def testParts(self):
        global piece
        self.assertTrue(self.p_id in piece.Parts)
        self.assertEqual(self.p_name, piece.Parts[self.p_id].name)

    def testMeasures(self):
        self.assertTrue(self.m_num in piece.Parts[self.p_id].measures)

class testTremolo(xmlSet):
    def setUp(self):
        self.p_id = "P1"
        if hasattr(self, "measure_id"):
            self.measure = piece.Parts[self.p_id].measures[self.measure_id]
        if hasattr(self, "item_id"):
            self.item = self.measure.notes[1][self.item_id]
        if hasattr(self, "notation_id"):
            if self.type == "stop":
                self.notation = self.item.postnotation[self.notation_id]
            else:
                self.notation = self.item.prenotation[self.notation_id]

    def testHasNotations(self):
        if hasattr(self, "item"):
            if not hasattr(self, "notate_num"):
                if self.type == "stop":
                    self.assertEqual(1, len(self.item.postnotation))
                else:
                    self.assertEqual(1, len(self.item.prenotation))
            else:
                if self.type == "stop":
                    self.assertEqual(self.notate_num, len(self.item.postnotation))
                else:
                    self.assertEqual(self.notate_num, len(self.item.prenotation))

    def testNotationInstance(self):
        if hasattr(self, "notation"):
            self.assertIsInstance(self.notation, Ornaments.Tremolo)

    def testTremoloType(self):
        if hasattr(self, "notation"):
            self.assertEqual(self.type, self.notation.type)

    def testTremoloValue(self):
        if hasattr(self, "notation"):
            self.assertEqual(self.value, self.notation.value)

class testMeasure1Note1(testTremolo):
    def setUp(self):
        self.measure_id = 1
        self.item_id = 0
        self.notation_id = 0
        self.type = "single"
        self.value = 1
        testTremolo.setUp(self)

class testMeasure1Note2(testTremolo):
    def setUp(self):
        self.measure_id = 1
        self.item_id = 1
        self.notation_id = 0
        self.type = "single"
        self.value = 2
        testTremolo.setUp(self)

class testMeasure1Note3(testTremolo):
    def setUp(self):
        self.measure_id = 1
        self.item_id = 2
        self.notation_id = 0
        self.type = "single"
        self.value = 3
        testTremolo.setUp(self)

class testMeasure2Note1(testTremolo):
    def setUp(self):
        self.measure_id = 2
        self.item_id = 0
        self.notation_id = 0
        self.type = "start"
        self.value = 2
        testTremolo.setUp(self)

class testMeasure2Note2Notation0(testTremolo):
    def setUp(self):
        self.measure_id = 2
        self.item_id = 1
        self.notation_id = 0
        self.type = "stop"
        self.value = 2
        self.notate_num = 1
        testTremolo.setUp(self)