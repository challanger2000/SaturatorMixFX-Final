#pragma once

#include "pluginterfaces/base/funknown.h"
#include "pluginterfaces/vst/vsttypes.h"

namespace SaturatorMixFX {

// Dedicated IDs for the Studio One Mix FX build. Keep separate from the normal Channel VST3.
static const Steinberg::FUID kProcessorUID (0xE31C8403, 0xA6C65716, 0xA0A991FE, 0xBBD41869);
static const Steinberg::FUID kControllerUID (0x32430640, 0x07325598, 0x89D7B1F7, 0xCD066E49);

constexpr Steinberg::Vst::ParamID kParamOnOff      = 99;
constexpr Steinberg::Vst::ParamID kParamDrive      = 100;
constexpr Steinberg::Vst::ParamID kParamCharacter  = 101;
constexpr Steinberg::Vst::ParamID kParamMix        = 102;
constexpr Steinberg::Vst::ParamID kParamOutput     = 103;

enum Character : int32_t {
    kTriode = 0,
    kPentode = 1,
    kIron = 2
};

} // namespace SaturatorMixFX
