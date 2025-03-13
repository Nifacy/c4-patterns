package com.patterns.lens;

import java.util.List;

import org.json.JSONArray;
import org.json.JSONObject;

import com.patterns.lens.info.fields.FieldArray;
import com.patterns.lens.info.fields.SchemaField;
import com.patterns.lens.info.fields.SingleField;

class FieldSerializer {

    public JSONObject serialize(SingleField field) {
        JSONObject dumpedField = new JSONObject();

        dumpedField.put("name", field.getName());
        dumpedField.put("optional", field.isOptional());

        return dumpedField;
    }

    public JSONObject serialize(FieldArray array) {
        JSONObject dumpedArray = new JSONObject();
        JSONArray dumpedElementFields = serialize(array.getElementFields());

        dumpedArray.put("name", array.getName());
        dumpedArray.put("fields", dumpedElementFields);

        return dumpedArray;
    }

    public JSONArray serialize(List<SchemaField> fields) {
        JSONArray dumpedFields = new JSONArray();

        for (SchemaField field : fields) {
            if (field instanceof SingleField) {
                dumpedFields.put(serialize((SingleField) field));
            } else if (field instanceof FieldArray) {
                dumpedFields.put(serialize((FieldArray) field));
            } else {
                throw new IllegalArgumentException("Unsupported field type: " + field);
            }
        }

        return dumpedFields;
    }
}
