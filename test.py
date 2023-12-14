def updateArrayOld(baseArray, updateArray):
    updateDict = {}
    for item in updateArray:
        key = (item['date'], item['subpage'])
        updateDict[key] = item

    print(updateDict)
    
    for i in range(len(baseArray)):
        key = (baseArray[i]['date'], baseArray[i]['subpage'])
        if key in updateDict:
            print(key)
            baseArray[i] = updateDict[key]
    return baseArray

def updateArray(baseArray, updateArray):
    # My previous version was O(n^2), but this one is O(n).
    # Thanks, ChatGPT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    baseDict = {}
    for item in baseArray:
        key = (item['date'], item['subpage'])
        baseDict[key] = item

    updateDict = {}
    for item in updateArray:
        key = (item['date'], item['subpage'])
        updateDict[key] = item

    print(baseDict)
    
    for i in range(len(updateArray)):
        key = (updateArray[i]['date'], updateArray[i]['subpage'])
        if key not in baseDict:
            print(key)
            baseArray.append(updateDict[key])
    return baseArray


array1 = [
{"date": "dog", "subpage": "rover", "color":"brown"},
{"date": "dog", "subpage": "fido"},
]

array2 = [
{"date": "dog", "subpage": "rover"},
{"date": "dog", "subpage": "fido"},
{"date": "dog", "subpage": "garrigus"}
]

print("Array 1")
print(array1)
print("Array 2")
print(array2)

print(updateArray(array1, array2))