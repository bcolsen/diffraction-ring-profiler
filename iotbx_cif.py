def run():

    import iotbx.cif
    import sys
#    print sys.argv

    cif_structure_list = iotbx.cif.reader(sys.argv[1]).build_crystal_structures()
    cif_structure = cif_structure_list.values()[0]
    cif_structure.scattering_type_registry(table="it1992")

    # Now calculate some structure factors
    f_calc = cif_structure.structure_factors(d_min=float(sys.argv[2])).f_calc()
    
    f_calc_sq = f_calc.as_intensity_array()
    if sys.argv[3] == 'sf':
        #print f_calc_sq
        f_calc_sq.show_array()
    if sys.argv[3] == 'ds':
        f_calc_sq.d_spacings().show_array()
    if sys.argv[3] == 'mt':
        #f_calc_sq.show_summary()
        f_calc_sq.multiplicities().show_array()
#        miller = cif_structure.build_miller_set(anomalous_flag=False, d_min = float(sys.argv[2]), d_max=None)
#        print miller.all_selection().show_array()
        
  
if __name__ == "__main__":
    run()
