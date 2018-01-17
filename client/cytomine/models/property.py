# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2017. Authors: see NOTICE file.
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
__copyright__ = "Copyright 2010-2017 University of Liège, Belgium, http://www.cytomine.be/"

# class ProjectProperty(Model):
#
#     def __init__(self, params = None):
#         super(ProjectProperty, self).__init__(params)
#         self._callback_identifier = "property"
#
#     def to_url(self):
#         if hasattr(self, "domainIdent") and not hasattr(self, "id"):#new
#             return "project/%d/property.json" % self.domainIdent
#         elif hasattr(self, "domainIdent") and hasattr(self, "id"):
#             return "project/%d/property/%d.json" % (self.domainIdent, self.id)
#
#     def __str__( self ):
#         return "Project Property %d,%d " % (self.project, self.id)


# class AnnotationProperty(Model):
#     def __init__(self, params=None):
#         super(AnnotationProperty, self).__init__(params)
#         self._callback_identifier = "property"
#
#     def to_url(self):
#         if hasattr(self, "domainIdent") and not hasattr(self, "id"):  # new
#             return "annotation/%d/property.json" % self.domainIdent
#         elif hasattr(self, "domainIdent") and hasattr(self, "id"):
#             return "annotation/%d/property/%d.json" % (self.domainIdent, self.id)
#
#     def __str__(self):
#         return "Annotation Property %d,%d " % (self.annotation, self.id)
#
#
# class AnnotationPropertyCollection(Collection):
#     def __init__(self, params=None):
#         super(AnnotationPropertyCollection, self).__init__(AnnotationProperty, params)
#
#     def to_url(self):
#         if hasattr(self, "annotation_id"):
#             return "annotation/%d/property.json" % self.annotation_id
#         else:
#             return None
#
#     def __str__(self):
#         return "Annotation Properties"
#
#         # class AnnotationCollection(Collection):
#
#     #    def __init__(self, params = None):
#     #       super(AnnotationCollection, self).__init__(Annotation, params)
#
#     #   def to_url(self):
#     #      if hasattr(self, "project"):
#     #         return "project/" + str(self.project) + "/annotation.json"
#     #     elif hasattr(self, "user") and hasattr(self, "imageinstance"):
#     #        return "user/" + str(self.user) + "/imageinstance/" + str(self.imageinstance) +  "/annotation.json"
#     #    elif hasattr(self, "imageinstance"):
#     #        return "imageinstance/" + str(self.imageinstance) +  "/userannotation.json"
#     #    else:
#     #        return "annotation.json"
#

# class AbstractImageProperty(Model):
#
#     def __init__(self, params = None):
#         super(AbstractImageProperty, self).__init__(params)
#         self._callback_identifier = "property"
#
#     def to_url(self):
#         if hasattr(self, "domainIdent") and not hasattr(self, "id"):#new
#             return "domain/be.cytomine.image.AbstractImage/%d/property.json" % self.domainIdent
#         elif hasattr(self, "domainIdent") and hasattr(self, "id"):
#             return "domain/be.cytomine.image.AbstractImage/%d/property/%d.json" % (self.domainIdent, self.id)
#
#     def __str__( self ):
#         return "Property %s,%s " % (self.domainClassName, self.domainIdent)
#
# class AbstractImagePropertyCollection(Collection):
#
#     def __init__(self, params = None):
#         super(AbstractImagePropertyCollection, self).__init__(AbstractImageProperty, params)
#
#     def to_url(self):
#         if hasattr(self, "abstract_image_id"):
#             return "domain/be.cytomine.image.AbstractImage/%d/property.json" % self.abstract_image_id
#         else:
#             return None
#
#     def __str__( self ):
#         return "AbstractImage Properties"