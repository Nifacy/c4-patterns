package io.github.nifacy.c4patterns.lens;

import org.json.JSONObject;

import io.github.nifacy.c4patterns.lens.info.PatternInfo;

class PatternInfoSerializer {

    private final FieldSerializer fieldSerializer;

    public PatternInfoSerializer() {
        this.fieldSerializer = new FieldSerializer();
    }

    public JSONObject serialize(PatternInfo info) {
        JSONObject dumpedInfo = new JSONObject();

        dumpedInfo.put("pluginName", info.getPluginName());
        dumpedInfo.put("docs", info.getDocumentation().orElse(""));
        dumpedInfo.put("params", this.fieldSerializer.serialize(info.getFields()));

        return dumpedInfo;
    }
}
