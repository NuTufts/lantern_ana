#ifndef __LANTERN_ANA_XSECFLUX_CALC_EVENTWEIGHT_VARIATIONS__
#define __LANTERN_ANA_XSECFLUX_CALC_EVENTWEIGHT_VARIATIONS__

#include "MapTypes.h"

class CalcEventWeightVariations {

 public:

  CalcEventWeightVariations() {};
  ~CalcEventWeightVariations() {};

  std::vector<double> calc( int num_variations,
			    std::vector<std::string>& included_par_list,
			    MapStringVecDouble& sys_weights );


};

#endif
