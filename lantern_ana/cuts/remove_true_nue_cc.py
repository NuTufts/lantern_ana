from lantern_ana.cuts.cut_factory import register_cut

@register_cut
def remove_true_nue_cc(ntuple, params):
    """
    we have to remove true nue cc events from bnb nu MC files in order to get the proper prediction.
    Otherwise, if we use the bnb intrinsice nue cc sample, then nue cc events are simulated twice.
    need to confirm if there is a volume constraint to this issue as well. 
    (i.e. are the intrinsic events generated only inside the TPC?)

    note: probably should change this to reverse logic to make less confusing.

    """
    if not params['ismc']:
        return False # do not remove

    apply_to_data = params.get('applyto')
    if type(apply_to_data) is not list:
        raise ValueError('applyto paramter for remove_true_nue_cc cut needs to be a list of strings')
    
    dataname = params['data_name']
    if dataname in apply_to_data:
        #print(f'this cut applies to the current data with name={dataname}')
        if ntuple.trueNuCCNC==0 and abs(ntuple.trueNuPDG)==12:
            return True # remove

    return False # do no remove