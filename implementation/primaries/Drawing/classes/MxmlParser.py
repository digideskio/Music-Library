import xml.sax
from xml.sax import make_parser, handler
import copy
try:
    from classes import Exceptions, Mark, Ornaments, Piece, Part, Harmony, Measure, Meta, Key, Meter, Note, Clef, Directions
    from classes.tree_cls import PieceTree, BaseTree
except:
    from implementation.primaries.Drawing.classes import Exceptions, Mark, Ornaments, Piece, Part, Harmony, Measure, Meta, Key, Meter, Note, Clef, Directions
    from implementation.primaries.Drawing.classes.tree_cls import PieceTree, BaseTree
# these define the current "things" we are handling: these are added on to relevant measures after being processed,
# because "staff" could be found anywhere whilst it's being processed and we need to know that to add it to the right object
note = None
direction = None
expression = None

# not sure whether still relevant, but globals for checking which degree/frame_note we are handling within the harmony section
degree = None
frame_note = None

#indicates current staff being loaded
staff_id = 1
voice = 1

# indicators of where we last found a repeat barline, and which staff, measure and part it was found in. Needed because we may
# have to modify it depending on what comes next
last_barline = None
last_fwd_repeat = None
last_barline_pos = {}

handleType = ""

def IdAsInt(index):
    if index is not None:
        try:
            return int(index)
        except:
            return index

def GetID(attrs, tag, val):
    # handy method which pulls out a nested id: attrs refers to a dictionary holding the id
    # tag refers to the tag we're looking at (e.g measure, part etc)
    # val refers to the exact index of the tag we're looking for (e.g number, id etc)
    # example case: attrs = self.attribs, tag=measure and val=number would return current measure number
    if tag in attrs:
        if val in attrs[tag]:
            return attrs[tag][val]
    return None

class MxmlParser(object):
    """this needs a huge tidy, but this class:
        sets up a few things that define where the tags get handled
        runs sax, which calls the parent methods according to what's happened
        the parent methods call the handlers defined in structure, or else figure out what handler to use. If there absolutely isn't one, nothing gets called
        spits out a piece class holding all this info.
    """
    def __init__(self, excluded=[]):
        # stuff for parsing. Tags refers to the xml tag list, chars refers to the content of each tag,
        # attribs refers to attributes of each tag, and handler is a method we call to work with each tag
        self.tags = []
        self.chars = {}
        self.attribs = {}
        self.handler = None

        # this will be put in later, but parser can take in tags we want to ignore, e.g clefs, measures etc.
        self.excluded = excluded

        # add any handlers, along with the tagname associated with it, to this dictionary
        self.structure = {"movement-title": SetupPiece, "credit": SetupPiece, "creator": SetupPiece, "defaults": SetupFormat, "part": UpdatePart,
             "score-part": UpdatePart, "part-group": UpdatePart, "measure": HandleMeasures, "note": CreateNote,
             "pitch":  HandlePitch, "unpitched": HandlePitch,"articulations":handleArticulation,
             "fermata": HandleFermata, "slur":handleOtherNotations, "lyric":handleLyrics,
             "technical": handleOtherNotations, "backup":HandleMovementBetweenDurations, "forward":HandleMovementBetweenDurations}

        # not sure this is needed anymore, but tags which we shouldn't clear the previous data for should be added here
        self.multiple_attribs = ["beats", "sign"]

        # any tags which close instantly in here
        self.closed_tags = ["technical","tie","dot","chord","note","measure","part",
                            "score-part","sound","print","rest","slur",
                            "accent","strong-accent","staccato",
                            "staccatissimo","up-bow","down-bow",
                            "cue"]
        self.end_tag = ["tremolo"]
        self.piece = PieceTree.PieceTree()
        self.d = False

    def Flush(self):
        self.tags = []
        self.chars = []
        self.attribs = {}

    def StartTag(self, name, attrs):
        if name not in self.excluded:
            if name in self.structure.keys():
                self.handler = self.structure[name]

            self.tags.append(name)
            if attrs is not None:
                self.attribs[name] = attrs
            self.d = CheckDynamics(name)
            if self.d and "dynamics" in self.tags:
                self.handler(self.tags, self.attribs, self.chars, self.piece)
            if name in self.closed_tags and self.handler is not None:
                self.handler(self.tags, self.attribs, self.chars, self.piece)
    def validateData(self, text):
        if text == "\n":
            return False
        for c in text:
            try:
                if str(c) != " ":
                    return True
            except:
                return False
        return False


    def NewData(self, text):
        sint = ignore_exception(ValueError)(int)
        if len(self.tags) > 0:
            if self.tags[-1] == "beat-type" or self.tags[-1] == "beats":
                if sint(text) is int:
                    self.chars[self.tags[-1]] = text

        if self.validateData(text):
            if len(self.tags) > 0:
                if self.tags[-1] not in self.chars:
                    self.chars[self.tags[-1]] = text
                else:
                    self.chars[self.tags[-1]] += text

    def CopyNote(self, part, measure_id, new_note):
        global voice
        # handles copying the latest note into the measure note list.
        # done at end of note loading to make sure staff_id is right as staff id could be encountered
        # any point during the note tag
        if part.getMeasure(measure_id, staff_id) is None:
            part.addEmptyMeasure(measure_id, staff_id)
        measure = part.getMeasure(measure_id, staff_id)
        voice_obj = measure.getVoice(voice)
        add = True
        notes = voice_obj.GetChildrenIndexes()
        for n in notes:
            no = voice_obj.GetChild(n)
            if new_note == no:
                add = False
                break
        if add:
            chord = False
            if hasattr(new_note, "chord"):
                chord = new_note.chord

            measure.addNote(new_note, voice, chord=chord)
            if hasattr(new_note, "MeasureRest") and new_note.MeasureRest:
                measure.rest = True
                voice_obj.rest = True


    def EndTag(self, name):
        global note, degree, frame_note, staff_id,direction,expression,last_barline,last_barline_pos, voice
        if self.handler is not None and not self.d:
            self.handler(self.tags, self.attribs, self.chars, self.piece)
        if name in self.tags:
            if len(self.tags) > 1:
                key = len(self.tags) - 2
                self.handler = None
                while key >= 0:
                    if self.tags[key] in self.structure:
                        self.handler = self.structure[self.tags[key]]
                        break
                    key -= 1

            else:
                self.handler = None
        if name in self.tags:
            self.tags.remove(name)
        if name == "direction":
            if direction is not None:
                measure_id = IdAsInt(GetID(self.attribs, "measure", "number"))
                part_id = GetID(self.attribs, "part", "id")
                part = self.piece.getPart(part_id)
                if part is not None:
                    if part.getMeasure(measure_id, staff_id) is None:
                        part.addEmptyMeasure(measure_id, staff_id)
                    measure = part.getMeasure(measure_id, staff_id)
                    measure.addDirection(copy.deepcopy(direction), voice)
                direction = None
            if expression is not None:
                measure_id = IdAsInt(GetID(self.attribs, "measure", "number"))
                part_id = GetID(self.attribs, "part", "id")
                part = self.piece.getPart(part_id)
                if part is not None:
                    if part.getMeasure(measure_id, staff_id) is None:
                        part.addEmptyMeasure(measure_id, staff_id)
                    measure = part.getMeasure(measure_id, staff_id)
                    measure.addExpression(copy.deepcopy(expression), voice)
                expression = None
            voice = 1
        if name == "barline":
            measure_id = IdAsInt(GetID(self.attribs, "measure", "number"))
            part_id = GetID(self.attribs, "part", "id")
            measure = self.piece.getPart(part_id).getMeasure(measure_id, staff_id).GetItem()
            if measure is not None:
                location = GetID(self.attribs, "barline", "location")
                last_barline_temp = measure.GetBarline(location)

                if hasattr(last_barline_temp, "repeat"):
                    if last_barline_temp.repeat == "forward":
                        last_fwd_repeat = last_barline_temp
                    last_barline = last_barline_temp
                    last_barline_pos = {"part":part_id,"measure":measure_id,"location":location}
        if name == "part":
            previous_part = GetID(self.attribs, "part", "id")
            if last_barline is not None:
                if last_barline.repeat == "forward":
                    last_barline.repeat += "-barline"
        if name == "measure":
            part_id = GetID(self.attribs, "part", "id")
            measure_id = IdAsInt(GetID(self.attribs, "measure", "number"))
            part = self.piece.getPart(part_id)
            if part is None:
                part = self.piece.getLastPart()
            part.CheckMeasureDivisions(measure_id)
            part.CheckMeasureMeter(measure_id)
            result = part.CheckIfTabStaff(measure_id)
            if result is not None:
                raise(Exceptions.TabNotImplementedException("Tab notation found: stopping"))
            staff_id = 1
            voice = 1
        if name in self.attribs:
            self.attribs.pop(name)
        if name in self.chars:
            self.chars.pop(name)

        if name == "note":
            measure_id = IdAsInt(GetID(self.attribs, "measure", "number"))
            part_id = GetID(self.attribs, "part", "id")
            part = self.piece.getPart(part_id)
            if part is None:
                part = self.piece.getLastPart()
            if part is not None:
                self.CopyNote(part, measure_id, copy.deepcopy(note))
            note = None
            voice = 1
        if name == "degree":
            degree = None
        if name == "frame-note":
            frame_note = None


    def parse(self, file):
        parser = make_parser()
        class Extractor(xml.sax.ContentHandler):
            def __init__(self, parent):
                self.parent = parent

            def startElement(self, name, attrs):
                attribs = {}
                for attrname in attrs.getNames():
                    attrvalue = attrs.get(attrname)
                    attribs[attrname] = attrvalue
                self.parent.StartTag(name, attribs)

            def characters(self, text):
                self.parent.NewData(text)

            def endElement(self, name):
                self.parent.EndTag(name)
        parser.setContentHandler(Extractor(self))
        # OFFLINE MODE
        parser.setFeature(handler.feature_external_ges, False)
        fob = open(file, 'r')
        parser.parse(fob)
        return self.piece

def YesNoToBool(entry):
    if entry == "yes":
        return True
    if entry == "no":
        return False

def ignore_exception(IgnoreException=Exception, DefaultVal=None):
    """ Decorator for ignoring exception from a function
    e.g.   @ignore_exception(DivideByZero)
    e.g.2. ignore_exception(DivideByZero)(Divide)(2/0)
    borrowed from: http://stackoverflow.com/questions/2262333/is-there-a-built-in-or-more-pythonic-way-to-try-to-parse-a-string-to-an-integer
    """

    def dec(function):
        def _dec(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except IgnoreException:
                return DefaultVal

        return _dec

    return dec


def SetupPiece(tag, attrib, content, piece):
    global handleType
    return_val = None
    if content is not [] and len(tag) > 0:
        title = None
        composer = None
        if tag[-1] == "movement-title":
            return_val = 1
            if "movement-title" in content:
                title = content["movement-title"]
        if tag[-1] == "creator":
            return_val = 1
            if "creator" in attrib:
                if "type" in attrib["creator"]:
                    if attrib["creator"]["type"] == "composer":
                        if "creator" in content:
                            composer = content["creator"]
        if tag[-1] == "movement-title" or "creator":
            if not hasattr(piece.GetItem(), "meta"):
                piece.GetItem().meta = Meta.Meta(composer=composer, title=title)

            else:
                if composer is not None:
                    piece.GetItem().meta.composer = composer
                if title is not None:
                    piece.GetItem().meta.title = title
        if "credit" in tag:
            page = 0
            if "credit" in attrib:
                if "page" in attrib["credit"]:
                    page = int(attrib["credit"]["page"])
            if tag[-1] == "credit-type":
                handleType = content["credit-type"]
            if tag[-1] == "credit-words":
                x = None
                y = None
                size = None
                justify = None
                valign = None
                text = None
                if "credit-words" in attrib:
                    temp = attrib["credit-words"]

                    if "default-x" in temp:
                        x = float(temp["default-x"])
                    if "default-y" in temp:
                        y = float(temp["default-y"])
                    if "font-size" in temp:
                        size = float(temp["font-size"])
                    if "justify" in temp:
                        justify = temp["justify"]
                        if justify == "center" and handleType == "":
                            handleType = "title"
                        if justify == "right" and handleType == "":
                            handleType = "composer"
                    if "valign" in temp:
                        valign = temp["valign"]
                        if valign == "bottom" and handleType == "":
                            handleType = "rights"

                if "credit-words" in content:
                    text = content["credit-words"]

                if handleType == "":
                    credit = Directions.CreditText(page=page, x=x,y=y,size=size,justify=justify,valign=valign,text=text)
                    if not hasattr(piece.GetItem(), "meta"):
                        piece.GetItem().meta = Meta.Meta()
                    piece.GetItem().meta.AddCredit(credit)
                else:
                    if handleType == "composer":
                        if not hasattr(piece.GetItem().meta, "composer"):
                            piece.GetItem().meta.composer = text
                        else:
                            if text.replace(" ","") not in piece.GetItem().meta.composer.replace(" ","") and piece.GetItem().meta.composer.replace(" ","") not in text.replace(" ",""):
                                piece.GetItem().meta.composer += text
                    if handleType == "rights":
                        if not hasattr(piece.GetItem().meta, "copyright"):
                            piece.GetItem().meta.copyright = text
                        else:
                            if text.replace(" ","") not in piece.GetItem().meta.copyright.replace(" ","") and piece.GetItem().meta.copyright.replace(" ","") not in text.replace(" ",""):
                                piece.GetItem().meta.copyright += text
                    if handleType == "title":
                        if not hasattr(piece.GetItem().meta, "title"):
                            piece.GetItem().meta.title = text
                        else:
                            if text.replace(" ","") not in piece.GetItem().meta.title.replace(" ","") and piece.GetItem().meta.title.replace(" ","") not in text.replace(" ",""):
                                piece.GetItem().meta.title += text
                    if handleType == "page number":
                        if not hasattr(piece.GetItem().meta, "pageNum"):
                            piece.GetItem().meta.pageNum = True
                    handleType = ""
    return return_val


def UpdatePart(tag, attrib, content, piece):
    part_id = GetID(attrib, "part", "id")
    if part_id is None:
        part_id = GetID(attrib, "score-part", "id")
    return_val = None
    if len(tag) > 0:
        if "part-group" in tag:
            index = 0
            type = ""
            if "part-group" in attrib:
                if "number" in attrib["part-group"]:
                   index=int(attrib["part-group"]["number"])
                if "type" in attrib["part-group"]:
                    type = attrib["part-group"]["type"]
            if type != "":
                if type == "start":
                    piece.startGroup(index)
                if type=="stop":
                    piece.stopGroup(index)
        if "score-part" in tag:
            if part_id is None:
                raise(Exceptions.NoScorePartException("ERROR IN UPDATEPART: no score-part id found"))
            elif piece.getPart(part_id) is None:
                piece.addPart(Part.Part(), index=part_id)
                return_val = 1
            if "part-name" in tag:
                if "part-name" in content and part_id is not None:
                    piece.getPart(part_id).GetItem().name = content["part-name"]
                    return_val = 1
            if "part-abbreviation" in tag:
                if "part-abbreviation" in content and part_id is not None:
                    piece.getPart(part_id).GetItem().shortname = content["part-abbreviation"]

    return return_val

def handleArticulation(tag, attrs, content, piece):
    global note
    if len(tag) > 0:
        if "articulations" in tag:
            if note is not None:
                accent = None
                if tag[-1] == "accent":
                    accent = Mark.Accent()
                if tag[-1] == "strong-accent":
                    s_type = ""
                    if "strong-accent" in attrs:
                        if "type" in attrs["strong-accent"]:
                            s_type = attrs["strong-accent"]["type"]
                    accent = Mark.StrongAccent(type=s_type)
                if tag[-1] == "staccato":
                    accent = Mark.Staccato()
                if tag[-1] == "staccatissimo":
                    accent = Mark.Staccatissimo()
                if tag[-1] == "detached-legato":
                    accent = Mark.DetachedLegato()
                if tag[-1] == "tenuto":
                    accent = Mark.Tenuto()
                if tag[-1] == "breath-mark":
                    accent = Mark.BreathMark()
                if tag[-1] == "caesura":
                    accent = Mark.Caesura()
                if accent is not None:
                    if note.Search(type(accent)) is None:
                        note.addNotation(accent)
                    accent = None
            return 1
    return None

def HandleMovementBetweenDurations(tags, attrs, chars, piece):
    global staff_id, last_note
    measure_id = IdAsInt(GetID(attrs, "measure","number"))

    part_id = GetID(attrs, "part","id")
    if part_id is not None:
        if measure_id is not None:
            part = piece.getPart(part_id)
            if part.getMeasure(measure_id, staff_id) is None:
                part.addEmptyMeasure(measure_id, staff_id)
            measure = part.getMeasure(measure_id, staff_id)
            if "backup" in tags and tags[-1]=="duration":
                part.GetItem().CheckDivisions()
                measure.Backup(duration=int(chars["duration"]))
            if "forward" in tags and tags[-1] == "duration":
                part.GetItem().CheckDivisions()
                measure.Forward(duration=int(chars["duration"]))

def HandleFermata(tags, attrs, chars, piece):
    global note
    if "fermata" in tags:
        type = None
        symbol = None
        if "fermata" in attrs:
            if "type" in attrs["fermata"]:
                type = attrs["fermata"]["type"]
        if "fermata" in chars:
            symbol = chars["fermata"]
        fermata = Mark.Fermata(type=type, symbol=symbol)
        note.addNotation(fermata)
    return None

def handleOtherNotations(tag, attrs, content, piece):
    global note
    if len(tag) > 0:
        if "notations" in tag:
            if tag[-1] == "slur":
                if not hasattr(note, "slurs"):
                    note.slurs = {}

                notation = Directions.Slur()
                num = len(note.slurs)
                if "slur" in attrs and "placement" in attrs["slur"]:
                    notation.placement = attrs["slur"]["placement"]
                if "slur" in attrs and  "number" in attrs["slur"]:
                    num = int(attrs["slur"]["number"])

                if "slur" in attrs and "type" in attrs["slur"]:
                    notation.type = attrs["slur"]["type"]
                note.slurs[num] = notation
            if tag[-2] == "technical":
                text = None
                if tag[-1] in content:
                    text = content[tag[-1]]
                note.addNotation(Mark.Technique(type=tag[-1], symbol=text))

            return 1
    return None

def HandleMeasures(tag, attrib, content, piece):
    global items, notes, expressions, staff_id, direction, expression, voice
    part_id = GetID(attrib, "part", "id")
    measure_id = IdAsInt(GetID(attrib, "measure", "number"))
    part = None
    return_val = None
    global degree
    if len(tag) > 0 and "measure" in tag:
        if "staff" in tag:
                staff_id = int(content["staff"])
        if part_id is None:
            part_id = piece.root.GetChildrenIndexes()[-1]
        if part_id is not None:
            part = piece.getPart(part_id)
            if part is None:
                part_id = piece.root.GetChildrenIndexes()[-1]
                part = piece.getPart(part_id)
        measure = None
        if part is not None:
            measure = part.getMeasure(measure=measure_id, staff=staff_id)
            if measure is None:
                part.addEmptyMeasure(measure_id, staff_id)
                measure = part.getMeasure(measure_id, staff_id)
            if measure is not None:
                measure = measure.GetItem()
        if tag[-1] == "divisions" and measure is not None:
            measure.divisions = int(content["divisions"])
        if tag[-1] == "mode" and "key" in tag and measure is not None:
            if hasattr(measure, "key"):
                measure.key.mode = content["mode"]

            else:
                measure.key = Key.Key(mode=content["mode"])
            return_val = 1
        if tag[-1] == "fifths" and "key" in tag:
            if hasattr(measure, "key"):
                measure.key.fifths = content["fifths"]
            else:
                measure.key = Key.Key(fifths=int(content["fifths"]))
            return_val = 1

        if tag[-1] == "beats" and ("time" in tag or "meter" in tag):
            if hasattr(measure, "meter"):
                measure.meter.beats = int(content["beats"])
            else:
                measure.meter = Meter.Meter(beats=int(content["beats"]))
            return_val = 1
        if tag[-1] == "beat-type" and ("time" in tag or "meter" in tag):
            if hasattr(measure, "meter"):
                measure.meter.type= int(content["beat-type"])
            else:
                measure.meter = Meter.Meter(type=int(content["beat-type"]))
            return_val = 1
        if "clef" in tag:
            handleClef(tag,attrib,content,piece)
        if "transpose" in tag:
            if "diatonic" in tag:
                if hasattr(measure, "transpose"):
                    measure.transpose.diatonic = content["diatonic"]
                else:
                    measure.transpose = Measure.Transposition(diatonic=content["diatonic"])
            if "chromatic" in tag:
                if hasattr(measure, "transpose"):
                    measure.transpose.chromatic = content["chromatic"]
                else:
                    measure.transpose = Measure.Transposition(chromatic=content["chromatic"])
            if "octave-change" in tag:
                if hasattr(measure, "transpose"):
                    measure.transpose.octave = content["octave-change"]
                else:
                    measure.transpose = Measure.Transposition(octave=content["octave-change"])
            return_val = 1
        if "print" in tag:
            part = piece.getPart(part_id)
            staves = piece.getPart(part_id).GetChildrenIndexes()
            if "print" in attrib:
                if "new-system" in attrib["print"]:
                    for staff in staves:
                        if part.getMeasure(measure_id, staff) is None:
                            part.addEmptyMeasure(measure_id, staff)
                        measure= part.getMeasure(measure_id, staff).GetItem()
                        measure.newSystem = YesNoToBool(attrib["print"]["new-system"])
                if "new-page" in attrib["print"]:
                    for staff in staves:
                        if part.getMeasure(measure_id, staff) is None:
                            part.addEmptyMeasure(measure_id, staff)
                        measure= part.getMeasure(measure_id, staff).GetItem()
                        measure.newPage = YesNoToBool(attrib["print"]["new-page"])
            return_val = 1

        if "harmony" in tag:
            root = None
            kind = None
            bass = None
            if direction is None:
                direction = Harmony.Harmony(kind=kind)
            else:
                direction.kind = kind

            if "root" in tag:
                if not hasattr(direction, "root"):
                    root = Harmony.harmonyPitch()
                    direction.root = root
                else:
                    root = direction.root
                if tag[-1] == "root-step":
                    if "root-step" in content:
                        root.step = content["root-step"]
                if tag[-1] == "root-alter":
                    if "root-alter" in content:
                        root.alter = content["root-alter"]

            if "kind" in tag:
                if not hasattr(direction, "kind") or direction.kind is None:
                    kind = Harmony.Kind()
                    direction.kind = kind
                elif direction.kind is not None:
                    kind = direction.kind
                if "kind" in content:
                    kind.value = content["kind"]
                if "kind" in attrib:
                    if "text" in attrib["kind"]:
                        kind.text = attrib["kind"]["text"]
                    if "halign" in attrib["kind"]:
                        kind.halign = attrib["kind"]["halign"]
                    if "parenthesis-degrees" in attrib["kind"]:
                        kind.parenthesis = attrib["kind"]["parenthesis-degrees"]

            if tag[-1] == "voice":
                voice = int(content["voice"])

            if "bass" in tag:
                if not hasattr(direction, "bass"):
                    direction.bass = Harmony.harmonyPitch()
                if "bass-step" in tag and "bass-step" in content:
                    direction.bass.step = content["bass-step"]
                if "bass-alter" in tag and "bass-alter" in content:
                    direction.bass.alter = content["bass-alter"]
            frame = None

            if "degree" in tag:
                if degree is None:
                    degree = Harmony.Degree()
                    direction.degrees.append(degree)

                if "degree-value" in tag:
                    if "degree-value" in content:
                        degree.value = content["degree-value"]
                if "degree-alter" in tag:
                    if "degree-alter" in content:
                        degree.alter = content["degree-alter"]
                if "degree-type" in tag:
                    if "degree-type" in content:
                        degree.type = content["degree-type"]
                    if "degree-type" in attrib:
                        if "text" in attrib["degree-type"]:
                            degree.display = attrib["degree-type"]["text"]

            if "frame" in tag:
                if not hasattr(direction, "frame"):
                    direction.frame = Harmony.Frame()
                if "first-fret" in tag:
                    direction.frame.firstFret = True
                    if "first-fret" in content:
                        if "first-fret" not in attrib:
                            direction.frame.firstFret = [content["first-fret"]]
                        else:
                            direction.frame.firstFret = [content["first-fret"]]
                            if "text" in attrib["first-fret"]:
                                direction.frame.firstFret.append(attrib["first-fret"]["text"])
                if "frame-strings" in tag and "frame-strings" in content:
                    direction.frame.strings = content["frame-strings"]
                if "frame-frets" in tag and "frame-frets" in content:
                    direction.frame.frets = content["frame-frets"]
                if "frame-note" in tag:
                    global frame_note
                    if frame_note is None:
                        frame_note = Harmony.FrameNote()

                    if "string" in tag and "string" in content:
                        frame_note.string = content["string"]
                        direction.frame.notes[int(content["string"])] = frame_note
                    if "fret" in tag and "fret" in content:
                        frame_note.fret = content["fret"]
                    if "barre" in tag and "barre" in attrib:
                        frame_note.barre = attrib["barre"]["type"]
                    if "fingering" in tag and "fingering" in content:
                        frame_note.fingering = content["fingering"]
    handleBarline(tag, attrib, content, piece)
    HandleDirections(tag, attrib, content, piece)
    handleArticulation(tag, attrib, content, piece)

    return return_val

def handleClef(tag,attrib,content,piece):
    global staff_id
    staff = GetID(attrib, "clef", "number")
    if staff is not None:
        staff_id = int(staff)
    measure_id = IdAsInt(GetID(attrib,"measure","number"))

    part_id = GetID(attrib,"part","id")
    part = piece.getPart(part_id)
    if part is not None:
        measure = part.getMeasure(measure_id,staff_id)
        if measure is None:
            part.addEmptyMeasure(measure_id, staff_id)
            measure = part.getMeasure(measure_id,staff_id)
        if measure is not None:
            measure = measure.GetItem()
            sign = None
            line = None
            octave = None
            if tag[-1] == "sign":
                sign = content["sign"]
            if tag[-1] == "line":
                line = int(content["line"])
            if tag[-1] == "clef-octave-change":
                octave = int(content["clef-octave-change"])
            if not hasattr(measure, "clef"):
                measure.clef = Clef.Clef(sign=sign,line=line,octave_change=octave)
            else:
                if sign is not None:
                    measure.clef.sign = sign
                if line is not None:
                    measure.clef.line = int(line)
                if octave is not None:
                    measure.clef.octave_change = octave
    staff_id = 1

def handleBarline(tag, attrib, content, piece):
    part_id = GetID(attrib, "part", "id")
    measure_id = IdAsInt(GetID(attrib, "measure", "number"))
    measure = None
    if part_id is not None and measure_id is not None:
        part = piece.getPart(part_id)
        if part is None:
            part = piece.getLastPart()

        if part.getMeasure(measure_id, int(staff_id)) is None:
            part.addEmptyMeasure(measure_id, int(staff_id))
        node = part.getMeasure(measure_id, int(staff_id))
        measure = node.GetItem()
    if "barline" in tag and measure is not None:
        if not hasattr(measure, "barlines"):
            measure.barlines = {}
        barline = None
        style = None
        repeat = None
        ending = None
        if tag[-1] == "ending":
            btype = None
            number = None
            if "ending" in attrib:
                if "number" in attrib["ending"]:
                    if attrib["barline"]["location"] not in measure.barlines or not hasattr(measure.barlines[attrib["barline"]["location"]], "ending"):
                        num_str = attrib["ending"]["number"]
                        split = num_str.split(",")
                        number = int(split[-1])
                        if last_fwd_repeat is not None and number > 2:
                            last_fwd_repeat.repeatNum = number
                    else:
                        measure.barlines[attrib["barline"]["location"]].ending.number = int(attrib["ending"]["number"])
                if "type" in attrib["ending"]:
                    if attrib["barline"]["location"] not in measure.barlines or not hasattr(measure.barlines[attrib["barline"]["location"]], "ending"):
                        btype = attrib["ending"]["type"]
                    else:
                        measure.barlines[attrib["barline"]["location"]].ending.type = attrib["ending"]["type"]

            ending = Measure.EndingMark(type=btype, number=number)

            if attrib["barline"]["location"] in measure.barlines:
                measure.barlines[attrib["barline"]["location"]].ending = ending

        if tag[-1] == "bar-style":
                if attrib["barline"]["location"] not in measure.barlines:
                    style = content["bar-style"]
                else:
                    measure.barlines[attrib["barline"]["location"]].style = style
        if tag[-1] == "repeat":
            if "repeat" in attrib:
                if "direction" in attrib["repeat"]:
                    barline = measure.GetBarline(attrib["barline"]["location"])
                    repeat = attrib["repeat"]["direction"]
                    if hasattr(last_barline, "repeat"):
                        last_repeat = last_barline.repeat
                        if repeat == "backward" and last_repeat != "forward":
                            repeat += "-barline"
                        if repeat == "forward" and last_repeat == "backward-barline":
                            if part_id == last_barline_pos["part"] and int(last_barline_pos["measure"]) == measure_id-1:
                                if attrib["barline"]["location"] != last_barline_pos["location"]:
                                    last_barline.repeat += "-double"
                    else:
                        if repeat == "backward":
                            repeat += "-barline"

                    if barline is not None:
                        barline.repeat = repeat

        if attrib["barline"]["location"] not in measure.barlines:
            if barline is None:
                barline = Measure.Barline(style=style, repeat=repeat, ending=ending)
            measure.barlines[attrib["barline"]["location"]] = barline
def CheckID(tag, attrs, string, id_name):
    if string in tag:
        return attrs[string][id_name]


def CreateNote(tag, attrs, content, piece):
    global note, staff_id, voice
    ret_value = None

    if len(tag) > 0 and "note" in tag:

        if tag[-1] == "staff":
            staff_id = int(content["staff"])
        if "note" in tag and note is None:
            note = Note.Note()
            ret_value = 1
        if "note" in attrs:
            if "print-object" in attrs["note"]:
                result = YesNoToBool(attrs["note"]["print-object"])
                note.print = result
        if "rest" in tag:
            measure = GetID(attrs, "rest", "measure")
            if measure is not None:
                value = YesNoToBool(measure)
                note.MeasureRest = value
            note.rest = True
        if "cue" in tag:
            note.cue = True



        if tag[-1] == "grace":
            slash = False
            if "grace" in attrs:
                if "slash" in attrs["grace"]:
                    slash = YesNoToBool(attrs["grace"]["slash"])
            note.addNotation(Note.GraceNote(slash=slash, first=True))
        if tag[-1] == "duration" and "note" in tag:
            if not hasattr(note, "duration"):
                note.duration = float(content["duration"])

        if tag[-1] == "type":
            note.SetType(content["type"])

        if "dot" in tag:
            note.dotted = True
        if tag[-1] == "tie":
            note.AddTie(attrs["tie"]["type"])
        if "chord" in tag:
            note.chord = True
        if tag[-1] == "stem":
            note.stem = Note.Stem(content["stem"])
        if tag[-1] == "voice":
            voice = int(content["voice"])

        if tag[-1] == "beam":
            type = ""
            if "beam" in content:
                type = content["beam"]
            if "beam" in attrs:
                id = int(attrs["beam"]["number"])
            else:
                id = len(note.beams)
            note.addBeam(id, Note.Beam(type))


        if tag[-1] == "accidental":
            if not hasattr(note, "pitch"):
                note.pitch = Note.Pitch()
                if "accidental" in content:
                    note.pitch.accidental = content["accidental"]

            else:
                if "accidental" in content:
                    note.pitch.accidental = content["accidental"]
        if tag[-1] == "staff":
            staff_id = int(content["staff"])
    HandleNoteheads(tag, attrs, content, piece)
    HandleArpeggiates(tag, attrs, content, piece)
    HandleSlidesAndGliss(tag, attrs, content, piece)
    handleLyrics(tag, attrs, content, piece)
    handleOrnaments(tag, attrs, content, piece)
    handleOtherNotations(tag, attrs, content, piece)
    handleTimeMod(tag, attrs, content, piece)
    return ret_value

def HandleNoteheads(tags, attrs, content, piece):
    if "note" in tags:
        if tags[-1] == "notehead":
            note.notehead = Note.Notehead()
            if "notehead" in attrs:
                if "filled" in attrs["notehead"]:
                    filled = YesNoToBool(attrs["notehead"]["filled"])
                    note.notehead.filled = filled
            if "notehead" in content:
                note.notehead.type = content["notehead"]
def HandleArpeggiates(tags, attrs, content, piece):
    if len(tags) > 0:
        if tags[-1] == "arpeggiate":
            direction = None
            if "arpeggiate" in attrs:
                if "direction" in attrs["arpeggiate"]:
                    direction = attrs["arpeggiate"]["direction"]
            arpegg = Note.Arpeggiate(direction=direction)
            note.addNotation(arpegg)
        if tags[-1] == "non-arpeggiate":
            type = None
            if "non-arpeggiate" in attrs:
                if "type" in attrs["non-arpeggiate"]:
                    type = attrs["non-arpeggiate"]["type"]
            narpegg = Note.NonArpeggiate(type=type)
            note.addNotation(narpegg)

def HandleSlidesAndGliss(tags, attrs, content, piece):
    type = None
    number = None
    lineType = None
    if "slide" in tags or "glissando" in tags:
        if tags[-1] in attrs:
            if "type" in attrs[tags[-1]]:
                type = attrs[tags[-1]]["type"]
            if "line-type" in attrs[tags[-1]]:
                lineType = attrs[tags[-1]]["line-type"]
            if "number" in attrs[tags[-1]]:
                number = int(attrs[tags[-1]]["number"])
    if "slide" in tags:
        slide = Note.Slide(type=type, lineType=lineType, number=number)
        note.addNotation(slide)
    if "glissando" in tags:
        gliss = Note.Glissando(type=type, lineType=lineType, number=number)
        note.addNotation(gliss)

def handleOrnaments(tags, attrs, content, piece):
    global note
    if "ornaments" in tags:
        if tags[-1] == "inverted-mordent":
            note.addNotation(Ornaments.InvertedMordent())
        if tags[-1] == "mordent":
            note.addNotation(Ornaments.Mordent())
        if tags[-1] == "trill-mark":
            note.addNotation(Ornaments.Trill())
        if tags[-1] == "turn":
            note.addNotation(Ornaments.Turn())
        if tags[-1] == "inverted-turn":
            note.addNotation(Ornaments.InvertedTurn())
        if tags[-1] == "tremolo":
            type = None
            value = None
            if "tremolo" in attrs:
                if "type" in attrs["tremolo"]:
                    type = attrs["tremolo"]["type"]
            if "tremolo" in content:
                value = int(content["tremolo"])
            note.addNotation(Ornaments.Tremolo(type=type, value=value))

def SetupFormat(tags, attrs, text, piece):
    return None


def HandlePitch(tags, attrs, text, piece):
    return_val = None
    if len(tags) > 0:
        if "pitch" or "unpitched" in tags:
            if not hasattr(note, "pitch") and note is not None:
                note.pitch = Note.Pitch()
            if "unpitched" in tags:
                note.pitch.unpitched = True
            if "step" in tags[-1]:
                if "step" not in text:
                    note.pitch.step = text["display-step"]
                else:
                    note.pitch.step = text["step"]
                return_val = 1
            if tags[-1] == "alter":
                note.pitch.alter = text["alter"]
                return_val = 1
            if "octave" in tags[-1]:
                if "octave" not in text:
                    note.pitch.octave = text["display-octave"]
                else:
                    note.pitch.octave = text["octave"]
                return_val = 1
    return return_val

def HandleDirections(tags, attrs, chars, piece):
    global expressions, items, staff_id, direction, expression
    return_val = None
    if len(tags) == 0:
        return None

    if "direction" in tags:
        measure_id = IdAsInt(GetID(attrs, "measure","number"))
        part_id = GetID(attrs, "part", "id")
        measure = None
        if measure_id is not None and part_id is not None:
            measure_node = piece.getPart(part_id).getMeasure(measure_id, staff_id)
            if measure_node is None:
                piece.getPart(part_id).addEmptyMeasure(measure_id, staff_id)
                measure_node = piece.getPart(part_id).getMeasure(measure_id, staff_id)
            measure = measure_node.GetItem()
        placement = None
        if measure is None:
            return None
        if tags[-1] == "staff":
            staff_id = int(chars["staff"])
        if "direction" in attrs:
            if "placement" in attrs["direction"]:
                placement = attrs["direction"]["placement"]

        if tags[-1] == "words":
            return_val = 1

            size = None
            font = None
            text = None
            if "words" in chars:
                text = chars["words"]

            if "words" in attrs:
                if "font-size" in attrs["words"]:
                    size = attrs["words"]["font-size"]
                if "font-family" in attrs["words"]:
                    font = attrs["words"]["font-family"]
            direction = Directions.Direction(font=font,text=text,size=size,placement=placement)
        if tags[-1] == "voice":
            voice = int(chars["voice"])
        if tags[-1] == "rehearsal":
            return_val = 1

            size = None
            font = None
            text = chars["rehearsal"]

            if "words" in attrs:
                if "font-size" in attrs["words"]:
                    size = attrs["words"]["font-size"]
                if "font-family" in attrs["words"]:
                    font = attrs["words"]["font-family"]
            direction = Directions.RehearsalMark(font=font,text=text,size=size,placement=placement)
        if "metronome" in tags:
            if tags[-1] == "beat-unit":
                return_val = 1
                unit = chars["beat-unit"]
                if direction is None:
                    direction = Directions.Metronome(placement=placement,beat=unit)
                else:
                    direction.beat = unit
                    direction.placement = placement
                direction.text = str(direction.beat)
                if "metronome" in attrs:
                    if "font-family" in attrs["metronome"]:
                        direction.font = attrs["metronome"]["font-family"]
                    if "font-size" in attrs["metronome"]:
                        direction.size = attrs["metronome"]["font-size"]
                    if "parentheses" in attrs["metronome"]:
                        direction.parentheses = YesNoToBool(attrs["metronome"]["parentheses"])
            if tags[-1] == "per-minute":
                return_val = 1
                pm = chars["per-minute"]

                if direction is None:
                    direction = Directions.Metronome(min=pm)
                else:
                    direction.min = pm
                direction.text += " = " + direction.min
                if "metronome" in attrs:
                    if "font-family" in attrs["metronome"]:
                        direction.font = attrs["metronome"]["font-family"]
                    if "font-size" in attrs["metronome"]:
                        direction.size = float(attrs["metronome"]["font-size"])
                    if "parentheses" in attrs["metronome"]:
                        direction.parentheses = YesNoToBool(attrs["metronome"]["parentheses"])
        if tags[-1] == "wedge":
            w_type = None
            if "wedge" in attrs:
                if "type" in attrs["wedge"]:
                    w_type = attrs["wedge"]["type"]
            expression = Directions.Wedge(placement = placement,type=w_type)

        if len(tags) > 1:
            if tags[-2] == "dynamics":
                expression = Directions.Dynamic(placement=placement, mark=tags[-1])
        if "sound" in tags:
            return_val = 1
            if "sound" in attrs:
                if "dynamics" in attrs["sound"]:
                    measure.volume = attrs["sound"]["dynamics"]
                if "tempo" in attrs["sound"]:
                    measure.tempo = attrs["sound"]["tempo"]
        l_type = None
        if tags[-1] in ["wavy-line","octave-shift","pedal","bracket"]:
            if tags[-1] in attrs:
                if "type" in attrs[tags[-1]]:
                    l_type = attrs[tags[-1]]["type"]
        if "octave-shift" in tags:
            amount = None
            font = None
            if "octave-shift" in attrs:
                if "size" in attrs["octave-shift"]:
                    amount = int(attrs["octave-shift"]["size"])
                if "font" in attrs["octave-shift"]:
                    font = attrs["octave-shift"]["font"]
            direction = Directions.OctaveShift(type=l_type, amount=amount, font=font)


        if tags[-1] == "wavy-line":
            direction = Directions.WavyLine(type=l_type)
        if tags[-1] == "pedal":
            line = None
            if "pedal" in attrs:
                if "line" in attrs["pedal"]:
                    line = YesNoToBool(attrs["pedal"]["line"])
            direction = Directions.Pedal(line=line, type=l_type)
        if tags[-1] == "bracket":
            num = None
            ltype = None
            elength=None
            lineend=None
            if "bracket" in attrs:
                if "number" in attrs["bracket"]:
                    num = int(attrs["bracket"]["number"])
                if "line-type" in attrs["bracket"]:
                    ltype = attrs["bracket"]["line-type"]
                if "end-length" in attrs["bracket"]:
                    elength = int(attrs["bracket"]["end-length"])
                if "line-end" in attrs["bracket"]:
                    lineend = attrs["bracket"]["line-end"]
            direction = Directions.Bracket(lineEnd=lineend, elength=elength, type=l_type, ltype=ltype, number=num)
    HandleRepeatMarking(tags, attrs, chars, piece)

    return return_val

def HandleRepeatMarking(tags, attrs, chars, piece):
    global staff_id, last_note, direction
    if "direction" in tags or "forward" in tags:
        if tags[-1] == "voice":
            voice = int(chars["voice"])
        measure = None
        part_id = GetID(attrs, "part", "id")
        measure_id = IdAsInt(GetID(attrs, "measure","number"))
        if part_id is not None:
            if measure_id is not None:
                measure = piece.getPart(part_id).getMeasure(measure_id, staff_id).GetItem()

        if measure is not None:
            d_type = None

            if tags[-1] == "segno" or tags[-1] == "coda":
                d_type = tags[-1]
                direction = Directions.RepeatSign(type=d_type)

            if tags[-1] == "sound":
                if "sound" in attrs:
                    if "coda" in attrs["sound"]:
                        measure.coda = attrs["sound"]["coda"]
                    if "dacapo" in attrs["sound"]:
                        measure.dacapo = YesNoToBool(attrs["sound"]["dacapo"])
                    if "dalsegno" in attrs["sound"]:
                        measure.dalsegno = attrs["sound"]["dalsegno"]
                    if "fine" in attrs["sound"]:
                        measure.fine = YesNoToBool(attrs["sound"]["fine"])
                    if "segno" in attrs["sound"]:
                        measure.segno = attrs["sound"]["segno"]
                    if "tocoda" in attrs["sound"]:
                        measure.tocoda = attrs["sound"]["tocoda"]



def handleLyrics(tags, attrs, chars, piece):
    global note
    if "lyric" in tags:
        if not hasattr(note, "lyrics"):
            note.lyrics = {}
        number = len(note.lyrics)
        if "lyric" in attrs:
            if "number" in attrs["lyric"]:
                number = int(attrs["lyric"]["number"])
        if number not in note.lyrics:
            note.lyrics[number] = Directions.Lyric()
        if tags[-1] == "text":
            note.lyrics[number].text = chars["text"]
        if tags[-1] == "syllabic":
            note.lyrics[number].syllabic = chars["syllabic"]

def handleTimeMod(tags, attrs, chars, piece):
    if "notations" in tags:
        if tags[-1] == "tuplet":
            type = None
            bracket = None

            if "tuplet" in attrs:
                if "type" in attrs["tuplet"]:
                    type = attrs["tuplet"]["type"]
                if "bracket" in attrs["tuplet"]:
                    bracket = YesNoToBool(attrs["tuplet"]["bracket"])
            tuplet = Note.Tuplet(bracket=bracket, type=type)
            note.addNotation(tuplet)
    if "time-modification" in tags:
        if not hasattr(note, "timeMod"):
            note.timeMod = Note.TimeModifier()
        if tags[-1] == "actual-notes":
            note.timeMod.actual = int(chars["actual-notes"])
        if tags[-1] == "normal-notes":
            note.timeMod.normal = int(chars["normal-notes"])
    return None

def CheckDynamics(tag):
    return_val = False
    dmark = ["p","f"]
    if len(tag) == 1 and tag in dmark:
        return_val = True
    elif len(tag) == 2:
        if tag[-1] in dmark:
            if tag[0] == tag[-1] or tag[0] == "m":
                return_val = True
    if len(tag) > 2:
        val = tag[0]
        if val in dmark:
            for char in tag:
                if char == val:
                    return_val = True
                else:
                    return_val = False
    return return_val



