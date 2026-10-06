#include "controller.h"
#include "editor.h"
#include "pluginids.h"
#include "../../SMX3Common/State/Smx3VstStateIO.h"

#include "base/source/fstreamer.h"
#include "public.sdk/source/vst/vstparameters.h"

#include <cstring>
#if defined(SMX3_MAC_STATE_DIAGNOSTIC)
#include <cstdio>
#endif

namespace SaturatorMixFX {

using namespace Steinberg;
using namespace Steinberg::Vst;

tresult PLUGIN_API Controller::initialize(FUnknown* context) {
    auto result = EditControllerEx1::initialize(context);
    if (result != kResultOk)
        return result;

    // VST3 bypass convention: 0 = processing active, 1 = bypass.
    parameters.addParameter(STR16("Bypass"), nullptr, 1, 0.0,
        ParameterInfo::kCanAutomate | ParameterInfo::kIsBypass, kParamOnOff);

    parameters.addParameter(STR16("Drive"), nullptr, 0, 0.30,
        ParameterInfo::kCanAutomate, kParamDrive);

    auto* character = new StringListParameter(STR16("Character"), kParamCharacter);
    character->appendString(STR16("Triode"));
    character->appendString(STR16("Pentode"));
    character->appendString(STR16("Iron"));
    parameters.addParameter(character);

    parameters.addParameter(STR16("Mix"), STR16("%"), 0, 1.0,
        ParameterInfo::kCanAutomate, kParamMix);

    // 0.75 maps to 0 dB with the current -18..+6 dB processor range.
    parameters.addParameter(STR16("Output"), STR16("dB"), 0, 0.75,
        ParameterInfo::kCanAutomate, kParamOutput);

    return kResultOk;
}

tresult PLUGIN_API Controller::setComponentState(IBStream* state) {
    const auto decoded = StateV2::readFromStream(state);
    if (decoded.source == StateV2::Source::Invalid)
        return kResultFalse;

#if defined(SMX3_MAC_STATE_DIAGNOSTIC)
    std::fprintf(stderr, "SMX3 DIAG controller setComponentState source=%d bypass=%.17g\\n",
        static_cast<int>(decoded.source), decoded.params.bypass);
#endif
    setParamNormalized(kParamOnOff, decoded.params.bypass);
    setParamNormalized(kParamDrive, decoded.params.drive);
    setParamNormalized(kParamCharacter, decoded.params.character);
    setParamNormalized(kParamMix, decoded.params.mix);
    setParamNormalized(kParamOutput, decoded.params.output);
    return kResultOk;
}

IPlugView* PLUGIN_API Controller::createView(FIDString name) {
    if (name && std::strcmp(name, ViewType::kEditor) == 0)
        return new SMX3Editor(this);
    return nullptr;
}

} // namespace SaturatorMixFX
