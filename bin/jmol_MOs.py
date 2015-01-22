#!/usr/bin/python
"""
Automatic plotting of MOs with jmol.
"""
# TODO: input options

import lib_mo, error_handler, lib_file, theo_header, input_options

class mo_output:
    """
    Abstract base class for MO output.
    """
    def __init__(self, moc, jopt):
        self.moc = moc
        self.jopt = jopt
        self.outstr = ''
        
    def output(self, ofileh):
        self.pre()
        self.print_mos()
        self.post(ofileh)
        
    def mopath(self, mo):
        return "MO_%s.png"%mo
    
    def pre(self):
        raise error_handler.PureVirtualError()

    def print_mos(self):
        raise error_handler.PureVirtualError()

    def post(self, ofileh):
        ofileh.write(self.outstr)
        
class mo_output_jmol(mo_output):
    """
    MO output in standard jmol format.
    """
    def pre(self):
        if self.moc.mldfile != "":
            self.outstr += '\nload "' + self.moc.mldfile + '" FILTER "nosort"\n'
        self.outstr += "mo titleformat ''\n"
        if self.jopt['rot_best']:
            self.outstr += "rotate best\n"
        self.outstr += "background white\n" + "mo fill\n"
        self.outstr += "mo cutoff %.3f\n\n"%self.jopt['cutoff']
        
    def print_mos(self):
        for imo in self.moc.molist:
            self.outstr += "mo %s\n"%self.moc.moname(imo)
            self.outstr += "write image png \"%s\"\n"%(self.moc.mopath(imo))            
        
class mo_output_html(mo_output):
    """
    HTML file for visualizing the MOs created with jmol.
    """
    def pre(self):        
        self.htable = lib_file.htmltable(ncol=2)
        
    def print_mos(self):
        for imo in self.moc.molist:            
            el = '<img src="%s" "border="1" width="%i">'%(self.moc.mopath(imo), self.jopt['width'])
            el += self.moc.mo_extra(imo,pref="<br> MO %i:"%imo)
            self.htable.add_el(el)
        
    def post(self, ofileh):
        ofileh.write("<h2>Orbitals - %s</h2>\n"%self.moc.mldfile)
        self.htable.close_table()
        ofileh.write(self.htable.ret_table())        
        
class mo_output_tex(mo_output):
    """
    tex file for visualizing the MOs created with jmol.
    -> This has to be adjusted if it should be used here!
    """
    def __init__(self, moc, width=6., trim=[0.,0.,0.,0.]):
        mo_output.__init__(self, moc)
        self.outfile = open("%sorbitals.tex"%self.moc.ret_label(), "w")
        
        # take this out?
        self.igraphstr="["
        if not trim == [0.,0.,0.,0.]:
            self.igraphstr += "trim = %.2fcm %.2fcm %.2fcm %.2fcm, clip=true,"%(trim[0],trim[1], trim[2], trim[3])
        self.igraphstr += "width=%.2f cm]"%width

    def pre(self):
        print "Writing tex file %sorbitals.tex ..."%self.moc.ret_label(),
        
        self.outfile.write("\\documentclass[a4paper]{article}\n")
        self.outfile.write("\\usepackage[cm]{fullpage}\n\\usepackage{graphicx}\n\n")
        self.outfile.write("% trim: left, bottom, right, top\n")
        self.outfile.write("\\newcommand{\\incMO}{\\includegraphics[trim = 1.00cm 1.00cm 1.00cm 1.00cm, clip=true,width=6.00 cm]}\n\n")
        self.outfile.write("\\begin{document}\n\n")
        self.outfile.write("\\begin{figure}\n")
        self.outfile.write("\\caption{%s}\n"%self.moc.mldfile)
        self.outfile.write("\\begin{tabular}{c | c}\n")
        

    def print_mos(self):
        for imo in self.moc.molist:
            self.outfile.write("\\incMO{%s}"%(self.moc.mopath(imo)))
            # self.outfile.write("\\includegraphics%s{%s}"%(self.igraphstr, self.moc.mopath(imo)))
            if imo%2==0: self.outfile.write("&\n")
            else:
                self.outfile.write("\\\\\n")
                self.outfile.write(self.moc.mo_extra(imo-1,postf="&\n"))
                self.outfile.write(self.moc.mo_extra(imo,postf="\\\\\n"))

    def post(self):
        self.outfile.write("\\end{tabular}\n\\end{figure}\n\n")
        self.outfile.write("\\end{document}\n")
        self.outfile.close()
        
        print "finished."

        
class mocoll:
    def __init__(self, st_ind, en_ind, mldfile=""):
        self.mldfile = mldfile
        
        if not mldfile=="":
            self.moset = lib_mo.MO_set_molden(mldfile)
            self.moset.read(lvprt=0)
            maxmo = self.moset.ret_num_mo()
        else:
            maxmo = 10000
              
        self.molist = range(st_ind-1, min(en_ind, maxmo))
        
    def moname(self, imo):
        return str(imo+1)
        
    def mopath(self, imo):
        return "%sMO_%s.png"%(self.ret_label(),self.moname(imo))
        
    def mo_extra(self, imo, pref="", postf=""):
        if self.mldfile=="":
            return ""
        else:
            sym = self.moset.ret_sym(imo)
            try:
                ene, occ = self.moset.ret_eo(imo)
            except:
                print "\n ERROR: imo = %i"%imo
                print "ens:", self.moset.ens
                print "occs:", self.moset.occs
                raise
            return "%s %5s %.4f / %.4f %s"%(pref,sym,ene,occ,postf)
            
    def ret_label(self):
        if self.mldfile=="":
            return ""
        else:
            return self.mldfile.split('.')[0] + '_'
        
class mocollf(mocoll):
    """
    For frontier MOs.
    """
    def __init__(self, en_ind, mldfile=""):
        mocoll.__init__(self, 1, 2*en_ind, mldfile)
        
    def moname(self, imo):
        if imo==0:
            return "homo"
        elif imo==1:
            return "lumo"
        elif imo%2==0:
            return "homo-%i"%(imo/2)
        else:
            return "lumo+%i"%(imo/2)
            
    def mo_extra(self, imo, pref="", postf=""):
        if self.mldfile=="":
            return ""
        else:
            ihomo = self.moset.ret_ihomo()
            if imo%2==0:
                imo2 = ihomo - imo/2
            else:
                imo2 = ihomo + imo/2 + 1
            try:
                ene, occ = self.moset.ret_eo(imo2)
            except:
                print "\n ERROR: imo2 = %i"%imo2
                raise
            return "%s %.3f / %.3f %s"%(pref,ene,occ,postf)            

class jmol_options(input_options.write_options):
    def jmol_input(self):
        self.read_float('Cutoff value', 'cutoff', 0.05)
        
        print "Specification of the orbital indices to be plotted:"
        self.read_yn('Specification in terms of frontier orbitals', 'fr_mos')
        
        if not self['fr_mos']:
            self.read_int('First orbital index to be plotted', 'st_ind', 1)
            self.read_int('Last orbital index to be plotted',  'en_ind', 10)
        else:
            self.read_int('Number of frontier orbitals',  'en_ind', 3)
        
        self.read_yn('Use "rotate best" command (only available in Jmol 14)', 'rot_best')
        
        self.read_int('Width of images in output html file', 'width', 400)
        
def run():    
    print 'jmol_MOs.py [<mldfile> [<mldfile2> ...]]\n'
    
    mldfiles = sys.argv[1:]
    
    if len(mldfiles) == 0:
        print "No file specified, generating generic script"
        mldfiles = ['']
        pref = ''
    elif len(mldfiles) == 1:
        print "Analyzing the file:", mldfiles[0]
        pref = mldfiles[0] + '.'
    else:
        print "Analyzing the files:", mldfiles
        pref = 'multi.'
        
    jopt = jmol_options('jmol.in')
    jopt.jmol_input()
    
    jo = lib_file.wfile('%sjmol_orbitals.spt'%pref)
    ho = lib_file.htmlfile('%sorbitals.html'%pref)
    
    ho.pre('Orbitals')
    
    for mldfile in mldfiles:
        print 'Analyzing %s ...\n'%mldfile
        if not jopt['fr_mos']:
          moc = mocoll(jopt['st_ind'], jopt['en_ind'], mldfile)
        else:
          moc = mocollf(jopt['en_ind'], mldfile)

        moout = mo_output_jmol(moc, jopt)
        moout.output(jo)
        
        moh = mo_output_html(moc, jopt)
        moh.output(ho)
            
    jo.post(lvprt=1)
    print "  -> Now simply run \"jmol %s\" to plot all the orbitals.\n"%jo.name
    ho.post(lvprt=1)
    print "  -> View in browser."    
    
def run_old():
    print "%s <st_ind> <en_ind> [<mldfile> [<mldfile2> ...]]"%sys.argv[0]
    print "or:"
    print "%s -f <num_mo> [<mldfile> [<mldfile2> ...]]\n"%sys.argv[0]

    if len(sys.argv)<3: sys.exit()

    if sys.argv[1] == '-f':
      fr_mos = True    
    else:
      fr_mos = False
      st_ind = int(sys.argv[1])
    en_ind = int(sys.argv[2])

    if len(sys.argv)>=4: mldfiles = sys.argv[3:]
    else: mldfiles = [""]

    jo = lib_file.wfile('jmol_orbitals.spt')
    ho = lib_file.htmlfile('orbitals.html')
    
    ho.pre('Orbitals')

    for mldfile in mldfiles:
        print 'Analyzing %s ...\n'%mldfile
        if not fr_mos:
          moc = mocoll(st_ind, en_ind, mldfile)
        else:
          moc = mocollf(en_ind, mldfile)

        moout = mo_output_jmol(moc)
        moout.output(jo)
        
        moh = mo_output_html(moc)
        moh.output(ho)
            
    jo.post(lvprt=1)
    print "  -> Now simply run \"jmol %s\" to plot all the orbitals.\n"%jo.name
    ho.post(lvprt=1)
    print "  -> View in browser."

if __name__=='__main__':
    import sys

    theo_header.print_header('Orbital plotting in Jmol')
    #run_old()
    run()