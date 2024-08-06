// @ts-nocheck
const iconsMap: Record<string, Element> = {
    string: 'symbol-text',
    numeric: 'symbol-numeric',
    float64: 'symbol-numeric',
    float32: 'symbol-numeric',
    boolean: 'symbol-boolean',
    date: 'calendar',
    timestamp: 'calendar',
    datetime: 'calendar',
    int64: 'symbol-numeric',
    int32: 'symbol-numeric',
    decimal: 'symbol-numeric',
    json: 'symbol-object',
    array: 'symbol-array',
};

export function getIconClassNamesForDataType(dataType: string | undefined) {
    if (!dataType) {
        return 'symbol-field';
    }

    const iconKey = iconsMap[dataType.toLowerCase()];
    if (!iconKey) {
        return 'symbol-field';
    }

    return iconKey;
}
