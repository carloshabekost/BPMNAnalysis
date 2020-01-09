from bs4 import BeautifulSoup
import pandas
import os

cwd = os.getcwd()

outerElements = ['startEvent', 'intermediateCatchEvent', 'intermediateThrowEvent', 'endEvent', 'exclusiveGateway',
                 'parallelGateway', 'complexGateway', 'eventBasedGateway', 'inclusiveGateway', 'task', 'sendTask',
                 'receiveTask', 'userTask', 'manualTask', 'businessRuleTask', 'serviceTask', 'scriptTask',
                 'callActivity', 'subProcess', 'dataObject', 'dataStoreReference', 'boundaryEvent', 'textAnnotation']
eventDefinitions = ['messageEventDefinition', 'timerEventDefinition', 'conditionalEventDefinition',
                    'signalEventDefinition', 'linkEventDefinition', 'escalationEventDefinition',
                    'compensateEventDefinition', 'errorEventDefinition', 'terminateEventDefinition',
                    'cancelEventDefinition']

eventDefinitions += [eventDefinitions[i] + 'NonInterrupting' for i in [0, 1, 2, 3, 5, 6, 7, 9]]

startEventDefinitions = eventDefinitions[0:4]
intermediateCatchEventDefinitions = eventDefinitions[0:5]
intermediateThrowEventDefinitions = [eventDefinitions[i] for i in [0, 3, 4, 5, 6]]
endEventDefinitions = [eventDefinitions[i] for i in [0, 3, 5, 6, 7, 8]]
boundaryEventDefinitions = [eventDefinitions[i] for i in [0, 1, 2, 3, 5, 6, 7, 9]] + [eventDefinitions[i] +
                                                                                      'NonInterrupting' for i in
                                                                                      [0, 1, 2, 3, 5, 6, 7, 9]]
taskDefinitions = ['multiInstanceLoopCharacteristics', 'standardLoopCharacteristics']
multiInstanceTypes = ['multiInstanceLoopSequential', 'multiInstanceLoopParallel']

subinfos = {'startEvent': startEventDefinitions, 'intermediateCatchEvent': intermediateCatchEventDefinitions,
            'intermediateThrowEvent': intermediateThrowEventDefinitions, 'endEvent': endEventDefinitions,
            'boundaryEvent': boundaryEventDefinitions}

dataframe_cols = ['regular'] + eventDefinitions + multiInstanceTypes + [taskDefinitions[-1]]
dataframe_cols = dataframe_cols

dataframe_index = outerElements + ['subProcess_' + x for x in outerElements]

paths = os.listdir(cwd)
paths = [os.path.join(cwd, x) for x in paths if x.endswith('.bpmn')]


def count_elements(df, element, subprocess=False):
    inner_df = pandas.DataFrame(0, index=dataframe_index, columns=dataframe_cols)
    rawcatch = {x: [] for x in outerElements}

    for outerElement in outerElements:
        rawcatch[outerElement] += element.find_all(outerElement)

    for k, v in rawcatch.items():
        index = k
        if subprocess:
            index = 'subProcess_' + k
        # print(k, v)
        if k == 'startEvent':
            total_inners = 0
            for startEvent in v:
                for inner in startEventDefinitions:
                    result = startEvent.find(inner)
                    if result:
                        inner_df.at[index, inner] += 1
                        total_inners += 1
            inner_df.at[index, 'regular'] = len(v) - total_inners
        if k == 'intermediateCatchEvent':
            for intermediateCatchEvent in v:
                for inner in intermediateCatchEventDefinitions:
                    result = intermediateCatchEvent.find(inner)
                    if result:
                        inner_df.at[index, inner] += 1
        if k == 'intermediateThrowEvent':
            for intermediateThrowEvent in v:
                for inner in intermediateThrowEventDefinitions:
                    result = intermediateThrowEvent.find(inner)
                    if result:
                        inner_df.at[index, inner] += 1
        if k == 'endEvent':
            total_inners = 0
            for endEvent in v:
                for inner in endEventDefinitions:
                    result = endEvent.find(inner)
                    if result:
                        inner_df.at[index, inner] += 1
                        total_inners += 1
            inner_df.at[index, 'regular'] = len(v) - total_inners
        if k.endswith('task') or k.endswith('Task') or k == 'callActivity':
            total_inners = 0
            for task in v:
                for inner in taskDefinitions:
                    if inner == 'multiInstanceLoopCharacteristics':
                        result = task.find(inner, {"isSequential": "true"})
                        if result:
                            inner_df.at[index, 'multiInstanceLoopSequential'] += 1
                            total_inners += 1
                        else:
                            result = task.find(lambda tag: tag.name == inner and not tag.attrs)
                            if result:
                                inner_df.at[index, 'multiInstanceLoopParallel'] += 1
                                total_inners += 1
                    elif inner == 'standardLoopCharacteristics':
                        result = task.find(inner)
                        if result:
                            inner_df.at[index, 'standardLoopCharacteristics'] += 1
                            total_inners += 1
            inner_df.at[index, 'regular'] = len(v) - total_inners
        if k == 'boundaryEvent':
            for boundaryEvent in v:
                for inner in boundaryEventDefinitions:
                    result = boundaryEvent.find(inner)
                    if result:
                        if boundaryEvent.has_attr("cancelActivity"):
                            inner_df.at[index, inner + 'NonInterrupting'] += 1
                        else:
                            inner_df.at[index, inner] += 1
        if k == 'subProcess':
            inner_df.at[index, 'regular'] += len(v)
            for subProcess in v:
                inner_df = count_elements(inner_df, subProcess, subprocess=True)
            # Adaptações para os elementos dos subprocessos (pot. recursivo) serão necessários
        if k.endswith('Gateway') or k == 'textAnnotation' or k == 'dataObject' or k == 'dataStoreReference':
            inner_df.at[index, 'regular'] += len(v)
    result_df = df + inner_df
    return result_df


def start_counts(pathways):
    for path in pathways:
        dataframe = pandas.DataFrame(0, index=dataframe_index, columns=dataframe_cols)
        with open(path, 'r') as file:
            content = "".join(file.readlines())
            soup = BeautifulSoup(content, 'xml')
            processes = soup.find_all('process')
            for process in processes:
                dataframe = count_elements(dataframe, process)
        path_to_csv = path.split('\\')[-1].split('.')[0] + '.csv'
        print(dataframe)
        print(path_to_csv)
        dataframe.to_csv(path_to_csv, sep=';')


# start_counts(paths)