from implementation.primaries.Drawing.tests.testHandlers import testclass
from implementation.primaries.Drawing.classes import Mark, MxmlParser, Directions, Part, Measure, Note
import unittest

class testHandleArticulation(testclass.TestClass):
    def setUp(self):
        testclass.TestClass.setUp(self)
        self.piece.addPart(index="P1", item=Part.Part())
        self.part = self.piece.getPart("P1")
        self.part.addEmptyMeasure(1, 1)
        measure = self.part.getMeasure(1, 1)
        MxmlParser.note = Note.Note()
        self.note = MxmlParser.note
        measure.addNote(MxmlParser.note)
        self.handler = MxmlParser.handleArticulation
        self.tags.append("articulations")
        self.data = {}


    def testNoData(self):
        self.tags.remove("articulations")
        self.assertEqual(None,self.handler(self.tags,self.attrs,self.chars,self.piece, self.data))

    def testIrrelevant(self):
        self.tags.remove("articulations")
        self.tags.append("what")
        self.assertEqual(None,self.handler(self.tags,self.attrs,self.chars,self.piece, self.data))

    def testRelevant(self):
        self.assertEqual(1, self.handler(self.tags,self.attrs,self.chars,self.piece, self.data))

    def testArticulationAccentTag(self):
        self.tags.append("accent")
        self.handler(self.tags,self.attrs,self.chars,self.piece, self.data)
        self.assertIsInstance(self.note.GetNotation(-1, "post"), Mark.Accent)

    def testArticulationAccentType(self):
        self.tags.append("accent")
        self.handler(self.tags,self.attrs,self.chars,self.piece, self.data)
        self.assertEqual("-",self.note.GetNotation(-1, "post").symbol)


    def testArticulationSaccentTag(self):
        self.tags.append("strong-accent")
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertIsInstance(self.note.GetNotation(-1, "post"), Mark.StrongAccent)

    def testArticulationStrongAccentTag(self):
        self.tags.append("strong-accent")
        self.attrs = {"type":"down"}
        self.handler(self.tags,self.attrs,self.chars,self.piece, self.data)
        self.assertEqual("V",self.note.GetNotation(-1, "post").symbol)

    def testStaccato(self):
        self.tags.append("staccato")
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertIsInstance(self.note.GetNotation(-1, "post"), Mark.Staccato)

    def testStaccatoSymbol(self):
        self.tags.append("staccato")
        self.handler(self.tags,self.attrs,self.chars,self.piece, self.data)
        self.assertEqual(".", self.note.GetNotation(-1, "post").symbol)

    def testStaccatissimo(self):
        self.tags.append("staccatissimo")
        self.handler(self.tags,self.attrs,self.chars,self.piece, self.data)
        self.assertIsInstance(self.note.GetNotation(-1, "post"), Mark.Staccatissimo)

    def testStaccatissimoSymbol(self):
        self.tags.append("staccatissimo")
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertEqual("triangle", self.note.GetNotation(-1, "post").symbol)

    def testDetachedLegato(self):
        self.tags.append("detached-legato")
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertIsInstance(self.note.GetNotation(-1, "post"), Mark.DetachedLegato)

    def testDetachedLegSymbol(self):
        self.tags.append("detached-legato")
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertEqual("lineDot", self.note.GetNotation(-1, "post").symbol)

    def testTenuto(self):
        self.tags.append("tenuto")
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertIsInstance(self.note.GetNotation(-1, "post"), Mark.Tenuto)

    def testTenutoSymbol(self):
        self.tags.append("tenuto")
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertEqual("line", self.note.GetNotation(-1, "post").symbol)

class testLyrics(testclass.TestClass):
    def setUp(self):
        testclass.TestClass.setUp(self)
        self.tags.append("note")
        self.tags.append("lyric")
        self.handler = MxmlParser.handleLyrics
        MxmlParser.note = Note.Note()
        self.data = {}

    def testLyricCreation(self):
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertTrue(hasattr(MxmlParser.note, "lyrics"))

    def testLyricNum(self):
        self.attrs["lyric"] = {"number": "1"}
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertTrue(1 in MxmlParser.note.lyrics.keys())

    def testLyricText(self):
        self.attrs["lyric"] = {"number": "1"}
        self.chars["text"] = "aaah"
        self.tags.append("text")
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertEqual("aaah", MxmlParser.note.lyrics[1].text)

    def testLyricSyllable(self):
        self.attrs["lyric"] = {"number": "1"}
        self.chars["syllabic"] = "single"
        self.tags.append("syllabic")
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertEqual("single", MxmlParser.note.lyrics[1].syllabic)

class testFermata(testclass.TestClass):
    def setUp(self):
        testclass.TestClass.setUp(self)
        self.tags.append("fermata")
        MxmlParser.note = Note.Note()
        self.handler = MxmlParser.HandleFermata
        self.data = {}

    def testFermata(self):
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertIsInstance(MxmlParser.note.GetNotation(-1, "post"), Mark.Fermata)

    def testFermataType(self):
        self.attrs["fermata"] = {"type": "inverted"}
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertEqual("inverted", MxmlParser.note.GetNotation(-1, "post").type)

    def testFermataSymbol(self):
        self.chars["fermata"] = "square"
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertEqual("square", MxmlParser.note.GetNotation(-1, "post").symbol)


class testSlurs(testclass.TestClass):
    def setUp(self):
        testclass.TestClass.setUp(self)
        self.tags.append("note")
        self.tags.append("notations")
        self.handler = MxmlParser.handleOtherNotations
        MxmlParser.note = Note.Note()
        self.data = {}

    def testNoData(self):
        self.tags.remove("note")
        self.tags.remove("notations")
        self.assertEqual(None, self.handler(self.tags,self.attrs,self.chars,self.piece, self.data))

    def testUnrelated(self):
        self.tags.remove("note")
        self.tags.remove("notations")
        self.tags.append("hello")
        self.assertEqual(None, self.handler(self.tags,self.attrs,self.chars,self.piece, self.data))

    def testRelated(self):
        self.assertEqual(1,self.handler(self.tags,self.attrs,self.chars,self.piece, self.data))

    def testSlur(self):
        self.tags.append("slur")
        self.handler(self.tags,self.attrs,self.chars,self.piece, self.data)
        self.assertTrue(hasattr(MxmlParser.note, "slurs"))
        self.assertEqual(Directions.Slur, type(MxmlParser.note.slurs[0]))


    def testSlurWithId(self):
        self.tags.append("slur")
        self.attrs = {"slur":{"number":"1"}}
        self.handler(self.tags,self.attrs,self.chars,self.piece, self.data)
        self.assertTrue(len(MxmlParser.note.slurs) == 1)

    def testSlurType(self):
        self.tags.append("slur")
        self.attrs["slur"] = {"type":"start"}
        self.handler(self.tags,self.attrs,self.chars,self.piece, self.data)
        self.assertTrue(hasattr(MxmlParser.note.slurs[0], "type"))
        self.assertEqual("start",MxmlParser.note.slurs[0].type)

    def testTwoSlursOfTheSameIndex(self):
        self.tags.append("slur")
        self.attrs["slur"] = {"number":"1","type":"start"}
        self.handler(self.tags,self.attrs,self.chars,self.piece, self.data)
        self.tags.append("slur")
        self.attrs["slur"] = {"number":"1","type":"stop"}
        self.handler(self.tags,self.attrs,self.chars,self.piece, self.data)
        self.assertEqual(MxmlParser.note.slurs[0].type, "start")
        self.assertEqual("stop",MxmlParser.note.slurs[1].type)

class t(testclass.TestClass):
    def setUp(self):
        testclass.TestClass.setUp(self)
        self.tags.append("note")
        self.tags.append("notations")
        self.handler = MxmlParser.handleOtherNotations
        MxmlParser.note = Note.Note()
        self.tags.append("technical")
        self.data = {"note": None, "direction": None}

class testpostnotation(t):
    def testNoData(self):
        self.tags.remove("notations")
        self.tags.remove("note")
        self.tags.remove("technical")
        self.assertIsNone(self.handler(self.tags,self.attrs,self.chars,self.piece, self.data))

    def testIrrelevant(self):
        self.tags.remove("technical")
        self.tags.remove("notations")
        self.tags.remove("note")
        self.tags.append("hello")
        self.assertIsNone(self.handler(self.tags,self.attrs,self.chars,self.piece, self.data))

class testClosedTechnique(t):
    def setUp(self):
        t.setUp(self)
        self.tag = ""

    def testCreated(self):
        self.tags.append(self.tag)
        self.handler(self.tags,self.attrs,self.chars,self.piece, self.data)
        self.assertIsInstance(MxmlParser.note.GetNotation(-1, "post"), Mark.Technique)

    def testTechniqueType(self):
        self.tags.append(self.tag)
        self.handler(self.tags,self.attrs,self.chars,self.piece, self.data)
        self.assertTrue(hasattr(MxmlParser.note.GetNotation(-1, "post"), "type"))
        self.assertEqual(self.tag,MxmlParser.note.GetNotation(-1, "post").type)

class testUpBow(testClosedTechnique):
    def setUp(self):
        testClosedTechnique.setUp(self)
        self.tag = "up-bow"

class testDownBow(testClosedTechnique):
    def setUp(self):
        testClosedTechnique.setUp(self)
        self.tag = "down-bow"

class testSnapPizz(testClosedTechnique):
    def setUp(self):
        testClosedTechnique.setUp(self)
        self.tag = "snap-pizzicato"

class testOpenTechnique(testClosedTechnique):
    def setUp(self):
        t.setUp(self)
        self.tag = ""
        self.value = ""

    def testTechniqueText(self):
        self.tags.append(self.tag)
        self.chars[self.tag] = self.value
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertEqual(self.value, MxmlParser.note.GetNotation(-1, "post").symbol)

class testFingering(testOpenTechnique):
    def setUp(self):
        testOpenTechnique.setUp(self)
        self.tag = "fingering"
        self.value = "0"

class testPluck(testOpenTechnique):
    def setUp(self):
        testOpenTechnique.setUp(self)
        self.tag = "pluck"
        self.value = "p"

class testString(testOpenTechnique):
    def setUp(self):
        testOpenTechnique.setUp(self)
        self.tag = "string"
        self.value = "0"


class testBend(t):

    def testBend(self):
        self.tags.append("technical")
        self.tags.append("bend")
        self.tags.append("bend-alter")
        self.chars["bend-alter"] = "6"
        self.handler(self.tags, self.attrs, self.chars, self.piece, self.data)
        self.assertEqual(6, MxmlParser.note.GetNotation(-1, "post").value)


