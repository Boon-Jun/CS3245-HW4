

def hasSkipPointer(item):
    return type(item) is tuple and len(item) == 4

def andDocLists(docList1, docList2):
    #docList1 AND docList2
    #docList is a list of [docId, tf-idf1, tf-idf2, ...]
    #returns a new list of docList [docId, tf-idf1, tf-idf2, ...]
    #docId will appear in both docList1 and docList2 and contains all tf-idf values from doclist1 and 2
    list1Size = len(docList1)
    list2Size = len(docList2)
    pos1 = 0;
    pos2 = 0;

    output = []

    while pos1 < list1Size and pos2 < list2Size:
        item1 = postList1[pos1]
        item2 = postList2[pos2]
        docId1 = item1[0]
        docId2 = item2[0]

        if docId1 == docId2:
            newItem = item1.extend(item2[1:-1])
            output.append(newItem)
            pos1 += 1
            pos2 += 1
        elif docId1 < docId2:
            pos1 += 1
        else:
            pos2 += 1
    return output

def andPosIndex(docLists, postList, window):
    #docLists AND postList
    #docLists is a list of [docId, [previous_term_positions]]
    #postList (docId, term_freq, posIndex, [skip pointer])
    #window specifies the maximum distance between 2 terms, hence allowing proximity search
    list1Size = len(docLists)
    list2Size = len(postList)
    pos1 = 0;
    pos2 = 0;

    output = []
    while pos1 < list1Size and pos2 < list2Size:
        item1 = docLists[pos1]
        item2 = postList[pos2]
        docId1 = item1[0]
        docId2 = item2[0]

        if docId1 == docId2:
            term_end_positions = []
            previous_term_positions = item1[1]
            posIndex = item2[2]
            for position in previous_term_positions:
                end_positions_set = set()
                for x in range(1, window + 1):
                    if (position + x) in posIndex and (position + x) not in end_positions_set:
                        end_positions_set.add(position + 1)
                        term_end_positions.append(position + 1)
            if len(term_end_positions) > 0:
                term_end_positions = sorted(term_end_positions)
                output.append([docId1, term_end_positions])#Keeps track of the ending position of a term
            pos1 += 1
            pos2 += 1
        elif docId1 < docId2:
            pos1 += 1
        else:
            if hasSkipPointer(item2) and postList[item2[3]] <= docId1:
                pos2 = item2[3]
            else:
                pos2 += 1
    return output

def orPosIndex(docList, postList):
    #docList OR postList2
    #docLists is a list of [docId, [term_positions]]
    list1Size = len(docList)
    list2Size = len(postList)
    pos1 = 0;
    pos2 = 0;

    output = []

    while pos1 < list1Size and pos2 < list2Size:
        item1 = docList[pos1]
        item2 = postList[pos2]
        docId1 = item1[0]
        docId2 = item2[0]

        if docId1 == docId2:
            oldPosIndex = item2[2]
            newPosIndex = item1[2]
            newPosIndex.extend(oldPosIndex)
            output.append([docId1, item1[1] + item2[1], newPosIndex])
            pos1 += 1
            pos2 += 1
        elif docId1 < docId2:
            output.append(item1)
            pos1 += 1
        else:
            output.append([docId2, item2[1], item2[2]])
            pos2 += 1

    while pos1 < list1Size:
        output.append(docList[pos1])
        pos1 += 1

    while pos2 < list2Size:
        item2 = postList[pos2]
        output.append([item2[0], item2[1], item2[2]])
        pos2 += 1

    return output
