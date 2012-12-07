# coding=UTF-8

import os
import subprocess
import re

from model import Type, Enum, Compound, Interface, Inheritable

class Sphinx:
    def __init__(self, model):
        self.model = model

    def prepare_gen(self):
        if not os.path.exists("gen"):
            os.makedirs("gen")

    def canon(self, string):
        return re.sub('[\.\[\]]', '_', string)

    def genref(self, name, primitive, type):
        link = ' <' + type + '_' + primitive + '>`'
        link = self.canon(link)
        return ':ref:`' + name + link

    def typeref(self, name, type):
        return self.genref(name, type, 'type')

    def primitiveref(self, name, primitive):
        return self.genref(name, primitive, 'primitive')

    def enumref(self, name, enum):
        return self.genref(name, enum, 'enum')

    def compoundref(self, name, compound):
        return self.genref(name, compound, 'compound')

    def interfaceref(self, name, interface):
        return self.genref(name, interface, 'interface')

    def shaperef(self, name, shape):
        return self.genref(name, shape, 'shape')

    def repref(self, name, rep):
        return self.genref(name, rep, 'rep')

    def primitiveref(self, name, primitive):
        return self.genref(name, primitive, 'primitive')

    def stripns(self, name):
        return re.sub('(.*)\.', '', name)

    def dump_typelist(self):
        self.prepare_gen()

        fr = open('types.rst','w')
        ft = open('gen/types.txt','w')

        header = """Data types
==========

.. csv-table:: Data types
    :header-rows: 1
    :file: gen/types.txt
    :delim: tab

"""

        typetmpl = """
.. index::
    {0}

.. _type_{0}:

{1}
{2}

{3}.

{4}

.. tabularcolumns:: |l|p{{4in}}|
.. csv-table:: {1} Details
    :header-rows: 1
    :file: {5}
    :delim: tab
    :widths: 5, 10

"""

        fr.write(header)
        ft.write('Name\tTypeID\n')

        types = list(self.model.type_names.keys())
        types.sort()
        for name in types:
            ctype = self.model.type_names[name]

            id = 'N/A'
            if isinstance(ctype, Type):
                id = ctype.typeid
                if id == -1:
                    id = 'None'
                else:
                    id = str(id)

            ft.write(ctype.name + '\t' + id + '\n')

            filename = 'gen/type-' + self.canon(ctype.name) + '.txt'
            fd = open(filename, 'w')
            fd.write('Property\tValue\n')
            if isinstance(ctype, Type):
                canonrep = 'None'
                if ctype.rep_canonical != None:
                    canonrep = self.typeref(self.stripns(ctype.rep_canonical), ctype.rep_canonical)
                repin = 'None'
                if len(ctype.rep_in) != 0:
                    repin = ', '.join([self.typeref(self.stripns(x), x) for x in ctype.rep_in])
                repout = 'None'
                if len(ctype.rep_out) != 0:
                    repout = ', '.join([self.typeref(self.stripns(x), x) for x in ctype.rep_out])
                fd.write('TypeID\t'+id+'\n')
                fd.write('Canonical representation\t'+canonrep+'\n')
                fd.write('Representations in\t'+repin+'\n')
                fd.write('Representations out\t'+repout+'\n')
            if isinstance(ctype, Inheritable):
                inherits = 'None'
                if len(ctype.inherits) != 0:
                    inherits = ', '.join([self.typeref(self.stripns(x.name), x.name) for x in ctype.inherits])
                    fd.write('Inherits\t'+inherits+'\n')



            fr.write(typetmpl.format(self.canon(ctype.name), ctype.name, '^' * len(ctype.name), ctype.desc, ctype.comment, filename))

        fr.close()
        ft.close()

    def dump_primitivelist(self):
        self.prepare_gen()

        fr = open('primitives.rst','w')

        header = """Fundamental data types
======================

The following defined types are used in the subsequent sections.
Implementors should treat these sizes as minimium requirements.

.. note::
    **Roger Leigh**  Depending upon how we wish to persue
    interoperability between implementations, these may be required to
    be exact.  Using plain text would mitigate this to an extent.

"""

        ptab = """
.. csv-table:: {0} Primitives
    :header-rows: 1
    :file: gen/primitives-{1}.txt
    :delim: tab

"""

        footer = """
.. tabularcolumns:: |l|l|p{3in}|
.. csv-table:: Shape state/attributes
    :header-rows: 1
    :file: spec/shapestate.txt
    :delim: tab
    :widths: 5, 2, 10

.. note::
    **Barry DeZonia** Support different coordinate spaces as needed
    (int, long, double).  Should be possible to iterate some regions.

"""
        fr.write(header)

        primitives = list(self.model.type_names.keys())
        primitives.sort()
        fh = dict()
        for name in primitives:
            primitive = self.model.type_names[name]

            if not isinstance(primitive, Type):
                continue

            for lang in primitive.types.keys():
                if lang not in fh.keys():
                    fh[lang] = open('gen/primitives-'+lang+'.txt','w')
                    if lang == 'raw':
                        fh[lang].write("Name\tBinType\tDescription\n")
                        fr.write(ptab.format('Raw', lang))
                    elif lang == 'c++':
                        fh[lang].write("Name\tC++ Type\n")
                        fr.write(ptab.format('C++', lang))
                    elif lang == 'java':
                        fh[lang].write("Name\tJava Type\n")
                        fr.write(ptab.format('Java', lang))
                    else:
                        fh[lang].write("Name\t"+lang+" Type\n")
                        fr.write(ptab.format(lang, lang))

                pname = primitive.name
                ptype = primitive.types[lang]

                if isinstance(primitive, Enum):
                    pname = self.enumref(primitive.name, primitive.name)
                    ptype = self.enumref(ptype, ptype)
                elif isinstance(primitive, Compound):
                    pname = self.compoundref(primitive.name, primitive.name)
                    ptype = self.compoundref(ptype, ptype)
                elif isinstance(primitive, Interface):
                    pname = self.interfaceref(primitive.name, primitive.name)
                    ptype = self.interfaceref(ptype, ptype)
                else:
                    pname = self.primitiveref(primitive.name, primitive.name)
                    ptype = self.primitiveref(ptype, ptype)

                if lang == 'raw':
                    fh[lang].write(pname + '\t' + ptype + '\t' +primitive.desc + '\n')
                else:
                    fh[lang].write(pname + '\t' + ptype + '\n')

        fr.write(footer)
        fr.close()

        for f in fh.values():
            f.close()

    def dump_enums(self):
        self.prepare_gen()

        fe = open('enums.rst','w')

        header="""Enumerated types
================

"""

        fe.write(header)

        names = list(self.model.type_names.keys())
        names.sort()
        for name in names:
            enum = self.model.type_names[name]

            if not isinstance(enum, Enum):
                continue

            filename = 'gen/enum-' + self.canon(enum.name) + '.txt'

            template = """
.. index::
    {0}

.. _enum_{0}:

{0}
{1}

.. csv-table:: {0}
    :header-rows: 1
    :file: {2}
    :delim: tab

"""
            fe.write(template.format(enum.name, '^' * len(enum.name), filename))

            symbols = False
            for sym in [x.symbol for x in enum.values.values()]:
                if sym != '':
                    symbols = True
            enumtab = open(filename, 'w')
            print('Writing '+ filename)
            if (symbols):
                enumtab.write('Name\tNumber\tSymbol\tDescription\n')
            else:
                enumtab.write('Name\tNumber\tSymbol\tDescription\n')

            values = list(enum.values.values())
            values.sort(key = lambda x: x.number)

            for val in values:
                enumtab.write(val.name + '\t' + str(val.number) + '\t')
                if (symbols):
                    enumtab.write(val.symbol + '\t')
                enumtab.write(val.desc + '\n')
            enumtab.close()

        fe.close()

    def dump_compounds(self):
        self.prepare_gen()

        fe = open('compounds.rst','w')

        header="""Compound types
==============

"""

        fe.write(header)

        names = list(self.model.type_names.keys())
        names.sort()
        for name in names:
            compound = self.model.type_names[name]
            if not isinstance(compound, Compound):
                continue

            templates = list(compound.templates.values())
            templates.sort(key = lambda x: x.seqno)

            members = list(compound.members.values())
            members.sort(key = lambda x: x.seqno)


            fullname = compound.name
            if len(templates) > 0:
                fullname += '<' + ', '.join([x.name for x in templates]) + '>'
            filename = 'gen/compound-' + self.canon(compound.name) + '.txt'

            template = """
.. index::
    {0}

.. _compound_{0}:

{1}
{2}

.. csv-table:: {1}
    :header-rows: 1
    :file: {3}
    :delim: tab

"""
            fe.write(template.format(self.canon(compound.name), fullname, '^' * len(fullname), filename))

            compoundtab = open(filename, 'w')
            print('Writing '+ filename)
            compoundtab.write('SeqNo\tType\tName\tDescription\n')

            for tp in templates:
                compoundtab.write('(T'+str(tp.seqno)+')' + '\t' + tp.type + '\t' +
                                  tp.name + '\t' +tp.desc + '\n')
            for mb in members:
                compoundtab.write(str(mb.seqno) + '\t' + mb.type + '\t' +
                                  mb.name + '\t' +mb.desc + '\n')
            compoundtab.close()

        fe.close()

    def dump_shapelist(self):
        self.prepare_gen()

        f = open('gen/shapes.txt','w')
        f.write("ID\tShape\tDims\tDescription\n")
        shapes = list(self.model.shape_ids.keys())
        shapes.sort()
        for id in shapes:
            shape = self.model.shape_ids[id]
            f.write(str(shape.id) + '\t:ref:`' + shape.name + ' <shape_' +
                    shape.name + '_' + shape.dim + '>`\t' +
                    shape.dim + '\t' + shape.desc + '\n')

    def dump_replist(self):
        self.prepare_gen()

        f = open('gen/representations.txt','w')
        f.write("ID\tRepresentation\tDims\tDescription\n")
        reps = list(self.model.representation_ids.keys())
        reps.sort()
        for id in reps:
            rep = self.model.representation_ids[id]
            f.write(str(rep.id) + '\t:ref:`' + rep.name + ' <rep_' +
                    rep.name + '_' + rep.dim + '>`\t' +
                    rep.dim + '\t' + rep.desc + '\n')

    def dump_shapereps(self):
        self.prepare_gen()

        shapes = list(self.model.shape_ids.keys())
        shapes.sort()
        shaperst = open('shapes.rst', 'w')
        print('Writing shapes.rst')
        header = """Shapes
======

Overview
--------

.. tabularcolumns:: |r|l|l|p{3in}|
.. csv-table:: Shapes
    :header-rows: 1
    :file: gen/shapes.txt
    :delim: tab
    :widths: 2, 5, 2, 10

Definitions
-----------

Note that in the following tables, a ‘\•’ indicates a representation
implemented *directly* by a shape, while ‘*(\•)*’ indicates a
representation implemented *indirectly* through inheriting another
shape's representations for in (or vice-versa for out).

"""
        shaperst.write(header)
        for id in shapes:
            shape = self.model.shape_ids[id]
            filename = 'gen/shape-' + shape.name + '-' + shape.dim + '.txt'
            shapetab = open(filename, 'w')
            print('Writing '+ filename)
            shapetab.write('Representation\tDim\tIn\tOut\tInherited from\n')
            reps = shape.reps()
            replist = list(reps.keys())
            replist.sort(key = lambda x: x.name+':'+x.dim)

            for r in replist:
                repval = reps[r]
                canonical = (r == shape.rep_canonical)
                name = r.name
                if (canonical):
                    name = '**' + name + '**'
                repins = [x.name for x in shape.rep_in]
                rin = ('', '\•', '*(\•)*')[shape.has_rep_in(r)]
                rout = ('', '\•', '*(\•)*')[shape.has_rep_out(r)]
                ishapes = [x.name + ' (' + x.dim + ')' for x in reps[r]]
                ishapes.sort()
                # Make this shape name bold
                shapename = shape.name + ' (' + shape.dim + ')'
                for i in range(len(ishapes)):
                    if (ishapes[i] == shapename):
                        ishapes[i] = '**' + ishapes[i] + '** [self]'
                inherit = ', '.join(ishapes)

                shapetab.write(self.repref(r.name, r.name, r.dim) + '\t' + r.dim + '\t' +
                               rin + '\t' + rout + '\t' + inherit + '\n')
            shapetab.close()
            
            template = """
.. index::
    {0} ({2})

.. _shape_{0}_{2}:

{0} ({2})
{1}

{3}.

{4}

.. tabularcolumns:: |l|l|c|c|p{{3in}}|
.. csv-table:: {0} representations ({2})
    :header-rows: 1
    :file: {5}
    :delim: tab
    :widths: 5, 2, 2, 2, 10

"""
            shaperst.write(template.format(shape.name, '^' * (len(shape.name) + len(shape.dim) + 3), shape.dim, shape.desc, shape.comment, filename))
            if (shape.rep_canonical):
                shaperst.write('Canonical form is ' + shape.rep_canonical.name + ' (' + shape.rep_canonical.dim + ').\n\n')

            # Sphinx definition
            clist = list(shape.inherit_comment.keys())
            clist.sort()
            for c in clist:
                comment = shape.inherit_comment[c]
                if (len(comment) > 0):
                    lines = comment.split('\n')
                    shaperst.write(c + '\n')
                    for line in lines:
                        shaperst.write('    ' + line + '\n')

        footer = """Relationships
-------------

The following figure illustrates the relationships detailed in the
above tables.  Ellipses are shapes, while representations are
rectangles.  Black arrows indicate inheritance of shape
representations, while red and blue arrows indicate the
representations possible to provide as input to and obtain as output
from a shape, respectively.

.. only:: html

    .. image:: gen/inherit-simple.svg
        :width: 100%
	:alt: Graph of canonical object relationships

.. only:: latex

    .. image:: gen/inherit-simple.pdf
        :width: 100%

.. only:: html

    .. image:: gen/inherit.svg
        :width: 100%
	:alt: Graph of object relationships

.. only:: latex

    .. image:: gen/inherit.pdf
        :width: 100%
"""

        shaperst.write(footer)
        shaperst.close()
        return

    def dump_repmembers(self):
        self.prepare_gen()

        reps = list(self.model.representation_ids.keys())
        reps.sort()
        reprst = open('representations.rst', 'w')
        print('Writing representations.rst')
        header="""Shape representations
=====================

Overview
--------

.. tabularcolumns:: |r|l|l|p{3.5in}|
.. csv-table:: Representations
    :header-rows: 1
    :file: gen/representations.txt
    :delim: tab
    :widths: 2, 5, 2, 10

Definitions
-----------

"""
        reprst.write(header)
        for id in reps:
            rep = self.model.representation_ids[id]
            filename = 'gen/rep-' + rep.name + '-' + rep.dim + '.txt'
            mtab = open(filename, 'w')
            print('Writing ' + filename)
            mtab.write('SeqNo\tName\tType\tDescription\n')
            members = rep.members
            mlist = list(members.keys())
            mlist.sort()

            for m in mlist:
                mval = members[m]
                mtab.write(str(mval.seq) + '\t' + mval.name + '\t' + mval.type + '\t' + mval.desc + '\n')
            mtab.close()

            template = """
.. index::
    {0} ({2})

.. _rep_{0}_{2}:

{0} ({2})
{1}

{3}.

{4}

.. tabularcolumns:: |r|l|l|p{{2in}}|
.. csv-table:: {0} members ({2})
    :header-rows: 1
    :file: {5}
    :delim: tab
    :widths: 2, 2, 5, 10

"""

            reprst.write(template.format(rep.name, '^' * (len(rep.name) + len(rep.dim) + 3), rep.dim, rep.desc, rep.comment, filename))

            template = """
{0}
    {1}

"""

            # Sphinx definition
            for m in mlist:
                mval = members[m]
                if (len(mval.comment) > 0):
                    lines = mval.comment.split('\n')
                    reprst.write(mval.name + '\n')
                    for line in lines:
                        reprst.write('    ' + line + '\n')

        reprst.close()
        return

    def dump_relgraph(self):
        self.prepare_gen()

        dot = open('gen/inherit.dot', 'w')
        print('Writing gen/inherit.dot')
        dot.write('digraph inheritance {\n')
#        dot.write('\tsize="4,8";\n')
        dot.write('\tnslimit=20;\n')
 #       dot.write('\tpage="6,8";\n')
#        dot.write('\tratio=fill;\n')
 #       dot.write('\taspect=0.75;')
        dot.write('\tmargin=0;\n')
        for rep in self.model.representation_ids.values():
            dot.write('\t"{0} ({1})" [shape=rectangle];\n'.format(rep.name, rep.dim))
        for shape in self.model.shape_ids.values():
            dot.write('\t"{0} ({1})" [shape=ellipse, style=filled, fillcolor="lightblue"];\n'.format(shape.name, shape.dim))
#            for i in shape.inherit_in:
#                dot.write('\t"{0} ({1})" -> "{2} ({3})";\n'.format(i.name, i.dim, shape.name, shape.dim))
#            for i in shape.inherit_out:
#                dot.write('\t"{0} ({1})" -> "{2} ({3})";\n'.format(shape.name, shape.dim, i.name, i.dim))
            for r in shape.reps_in():
                dot.write('\t"{0} ({1})" -> "{2} ({3})" [color=red];\n'.format(r.name, r.dim, shape.name, shape.dim))
            for r in shape.reps_out():
                dot.write('\t"{0} ({1})" -> "{2} ({3})" [color=blue];\n'.format(shape.name, shape.dim, r.name, r.dim))
        dot.write('}\n')
        dot.close()
        print('Generating gen/inherit.svg')
        subprocess.call(['sh', '-c', 'ccomps -x gen/inherit.dot | dot | gvpack -g | neato -n2 -Tsvg > gen/inherit.svg'])
        print('Generating gen/inherit.pdf')
        subprocess.call(['sh', '-c', 'ccomps -x gen/inherit.dot | dot | gvpack -g | neato -n2 -Tpdf > gen/inherit.pdf'])
        return

    def dump_relgraph_simple(self):
        self.prepare_gen()

        dot = open('gen/inherit-simple.dot', 'w')
        print('Writing gen/inherit-simple.dot')
        dot.write('digraph inheritance {\n')
        dot.write('\tnslimit=20;\n')
        dot.write('\tmargin=0;\n')
        reps = set()
        for shape in self.model.shape_ids.values():
            dot.write('\t"{0} ({1})" [shape=ellipse, style=filled, fillcolor="lightblue"];\n'.format(shape.name, shape.dim))
            if shape.rep_canonical != None:
                reps.add(shape.rep_canonical);
                dot.write('\t"{0} ({1})" -> "{2} ({3})" [color=blue];\n'.format(shape.name, shape.dim, shape.rep_canonical.name, shape.rep_canonical.dim))
        for rep in reps:
            dot.write('\t"{0} ({1})" [shape=rectangle];\n'.format(rep.name, rep.dim))
        dot.write('}\n')
        dot.close()
        print('Generating gen/inherit-simple.svg')
        subprocess.call(['sh', '-c', 'ccomps -x gen/inherit-simple.dot | dot | gvpack -g | neato -n2 -Tsvg > gen/inherit-simple.svg'])
        print('Generating gen/inherit-simple.pdf')
        subprocess.call(['sh', '-c', 'ccomps -x gen/inherit-simple.dot | dot | gvpack -g | neato -n2 -Tpdf > gen/inherit-simple.pdf'])
        return

    def dump(self):
        self.dump_typelist()
        self.dump_primitivelist()
        self.dump_enums()
        self.dump_compounds()
        # self.dump_shapelist()
        # self.dump_replist()
        # self.dump_shapereps()
        # self.dump_repmembers()
        # self.dump_relgraph()
        # self.dump_relgraph_simple()
