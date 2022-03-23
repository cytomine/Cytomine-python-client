# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2022. Authors: see NOTICE file.
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

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@uliege.be>", "Mormont Romain <r.mormont@uliege.be>"]
__copyright__ = "Copyright 2010-2022 University of Liège, Belgium, http://www.cytomine.be/"

from .model import Model, DomainModel
from .collection import Collection, DomainCollection
from .annotation import Annotation, AnnotationCollection, AnnotationTerm, AlgoAnnotationTerm
from .image import AbstractImage, AbstractImageCollection, AbstractSlice, AbstractSliceCollection,\
    ImageInstance, ImageInstanceCollection, SliceInstance, SliceInstanceCollection, \
    ImageServer, ImageServerCollection
#from .imagegroup import ImageGroup, ImageGroupCollection, ImageGroupImageInstance, ImageGroupImageInstanceCollection
#from .imagegroup import ImageGroup, ImageGroupCollection, ImageGroupHDF5, ImageSequence, ImageSequenceCollection
from .ontology import Ontology, OntologyCollection, Term, TermCollection, RelationTerm
from .project import Project, ProjectCollection, Discipline, DisciplineCollection
from .property import Property, PropertyCollection, AttachedFile, AttachedFileCollection, Description, \
    Tag, TagCollection, TagDomainAssociation, TagDomainAssociationCollection
from .track import Track, TrackCollection, AnnotationTrack
from .social import AnnotationAction, AnnotationActionCollection, Position, PositionCollection
from .software import Software, SoftwareCollection, SoftwareParameter, SoftwareParameterCollection, \
    SoftwareProject, SoftwareProjectCollection, Job, JobCollection, JobParameter, \
    JobParameterCollection, JobTemplate, JobData, SoftwareUserRepository, SoftwareUserRepositoryCollection, \
    ProcessingServer, ProcessingServerCollection, SoftwareParameterConstraint, SoftwareParameterConstraintCollection
from .storage import Storage, StorageCollection, UploadedFile, UploadedFileCollection
from .user import User, CurrentUser, UserJob, UserCollection, UserJobCollection, \
    Group, GroupCollection, UserGroup, UserGroupCollection, Role, RoleCollection, UserRole, UserRoleCollection
