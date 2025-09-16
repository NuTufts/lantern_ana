#include "calcEventWeightVariations.h"

std::vector<double> CalcEventWeightVariations::calc( int num_variations,
						     std::vector<std::string>& included_par_list,
						     MapStringVecDouble& sys_weights )
{

  std::vector<double> weights(num_variations,1.0);

  for ( auto const& it : sys_weights ) {
    bool found = false;
    std::string parname = it.first;
    for ( auto const& par : included_par_list ) {
      if ( par==parname ) {
	found = true;
	break;
      }
    }

    if ( !found ) {
      continue;
    }

    const std::vector<double>& variations = it.second;
    for ( size_t i=0; i<variations.size(); i++) {
      if ( i>num_variations )
	break;
      if ( variations[i]<10.0)
	weights[i] *= variations[i];
    }
  }

  return weights;
  
}
