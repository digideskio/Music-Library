\version "2.18.2" 
\version "2.18.2" 
ponestaffone = \new Staff \with {
instrumentName = \markup { 
 \column { 
 \line { "MusicXML Part" 
 } 
 } 
 } 
 }{\autoBeamOff % measure 1
\clef treble \key c \major 
\once \override Staff.TimeSignature.style = #'single-digit
\time 3/8 b'8[ b'8 b'8]  \bar "|."

 }

<<\ponestaffone>>