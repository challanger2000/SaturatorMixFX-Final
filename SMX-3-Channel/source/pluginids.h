#pragma once

#include "pluginterfaces/base/funknown.h"
#include "pluginterfaces/vst/vsttypes.h"

namespace SaturatorMixFX {

static const Steinberg::FUID kProcessorUID (0x86D3F3F0, 0xE7785981, 0x8ED1204F, 0x08A35C82);
static const Steinberg::FUID kControllerUID (0x17D4F54D, 0x0E35572C, 0x94A755F2, 0xF0BD2F7A);

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
