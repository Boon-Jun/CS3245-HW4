
def andOp(postList1, postList2):
    #postList1 AND postList2
    list1Size = len(postList1)
    list2Size = len(postList2)
    pos1 = 0;
    pos2 = 0;

    output = []

    while pos1 < list1Size and pos2 < list2Size:
        item1 = postList1[pos1]
        item2 = postList2[pos2]
        docId1 = item1[0] if hasSkipPointer(item1) else item1
        docId2 = item2[0] if hasSkipPointer(item2) else item2

        if docId1 == docId2:
            output.append(docId1)
            pos1 += 1
            pos2 += 1
        elif docId1 < docId2:
            if hasSkipPointer(item1) and postList1[item1[1]] <= docId2:
                pos1 = item1[1]
            else:
                pos1 += 1
        else:
            if hasSkipPointer(item2) and postList2[item2[1]] <= docId1:
                pos2 = item2[1]
            else:
                pos2 += 1
    return output

def orOp(postList1, postList2):
    #postList1 OR postList2
    list1Size = len(postList1)
    list2Size = len(postList2)
    pos1 = 0;
    pos2 = 0;

    output = []

    while pos1 < list1Size and pos2 < list2Size:
        item1 = postList1[pos1]
        item2 = postList2[pos2]
        docId1 = item1[0] if hasSkipPointer(item1) else item1
        docId2 = item2[0] if hasSkipPointer(item2) else item2

        if docId1 == docId2:
            output.append(docId1)
            pos1 += 1
            pos2 += 1
        elif docId1 < docId2:
            output.append(docId1)
            pos1 += 1
        else:
            output.append(docId2)
            pos2 += 1

    while pos1 < list1Size:
        docId1 = postList1[pos1][0] if hasSkipPointer(postList1[pos1]) else postList1[pos1]
        output.append(docId1)
        pos1 += 1

    while pos2 < list2Size:
        docId2 = postList2[pos2][0] if hasSkipPointer(postList2[pos2]) else postList2[pos2]
        output.append(docId2)
        pos2 += 1

    return output

def notOp(postList1, postList2):
    #postList1 AND NOT postList2
    list1Size = len(postList1)
    list2Size = len(postList2)
    pos1 = 0;
    pos2 = 0;

    output = []

    while pos1 < list1Size and pos2 < list2Size:
        item1 = postList1[pos1]
        item2 = postList2[pos2]
        docId1 = item1[0] if hasSkipPointer(item1) else item1
        docId2 = item2[0] if hasSkipPointer(item2) else item2

        if docId1 < docId2:
            output.append(docId1)
            pos1 += 1
        elif docId1 == docId2:
            pos1 += 1
            pos2 += 1
        else:
            if hasSkipPointer(item2) and postList2[item2[1]] <= docId1:
                pos2 = item2[1]
            else:
                pos2 += 1

    while pos1 < list1Size:
        docId1 = postList1[pos1][0] if hasSkipPointer(postList1[pos1]) else postList1[pos1]
        output.append(docId1)
        pos1 += 1

    return output

def hasSkipPointer(item):
    return type(item) is tuple
