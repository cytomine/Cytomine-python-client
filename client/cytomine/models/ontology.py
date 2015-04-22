# -*- coding: utf-8 -*-

#
# * Copyright (c) 2009-2015. Authors: see NOTICE file.
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *      http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# */

__author__          = "Stévens Benjamin <b.stevens@ulg.ac.be>" 
__contributors__    = ["Marée Raphaël <raphael.maree@ulg.ac.be>", "Rollus Loïc <lrollus@ulg.ac.be"]                
__copyright__       = "Copyright 2010-2015 University of Liège, Belgium, http://www.cytomine.be/"


from model import Model
from collection import Collection


class Sample(Model):

    def __init__(self, params = None):
        super(Sample, self).__init__(params)
        self._callback_identifier = "sample"

    def to_url(self):
        if hasattr(self, "id"):
            return "sample/%d.json" % self.id
        else:
            return "sample.json"

    def __str__( self ):
        return str(self.id) + " : " + str(self.name)

                
class Ontology(Model):

    def __init__(self, params = None):
        super(Ontology, self).__init__(params)
        self._callback_identifier = "ontology"

    def to_url(self):
        if hasattr(self, "id"):
            return "ontology/%d.json" % self.id
        else:
            return "ontology.json"

    def __str__( self ):
        return "ontology : " + str(self.id)

class Term(Model):

    def __init__(self, params = None):
        super(Term, self).__init__(params)
        self._callback_identifier = "term"

    def to_url(self):
        if hasattr(self, "id"):
            return "term/%d.json" % self.id
        else:
            return "term.json"

    def __str__( self ):
        return str(self.id) + " : " + str(self.name)

class RelationTerm(Model):

    def __init__(self, params = None):
        super(RelationTerm, self).__init__(params)
        self.is_new = False
        self._callback_identifier = "relationterm"

    def to_url(self):
        if self.is_new:
            return "relation/parent/term.json"
        else: 
            return "relation/parent/term1/%d/term2/%d.json" % (self.term1, self.term2)

    def __str__( self ):
        return "parent : %d, child : %d " % (self.term1, self.term2)

class TermCollection(Collection):

    def __init__(self, params = None):
        super(TermCollection, self).__init__(Term, params)

    def to_url(self):
        if hasattr(self, "ontology"):
            return "ontology/" + str(self.ontology) + "/term.json"
        return "term.json"        
