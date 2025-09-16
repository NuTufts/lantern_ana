#ifdef __CINT__

#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;

// STL containers
#pragma link C++ class std::vector<double>+;
#pragma link C++ class std::map<std::string, std::vector<double> >+;
#pragma link C++ class std::pair<const std::string, std::vector<double> >+;
#pragma link C++ typedef MapStringVecDouble;
#pragma link C++ class CalcEventWeightVariations+;

#endif
