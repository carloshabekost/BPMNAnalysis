from bs4 import BeautifulSoup
import PySimpleGUI as psg
import pandas
import os


# cwd = os.getcwd()

outerElements = ['startEvent', 'intermediateCatchEvent', 'intermediateThrowEvent', 'endEvent', 'exclusiveGateway',
                 'parallelGateway', 'complexGateway', 'eventBasedGateway', 'inclusiveGateway', 'task', 'sendTask',
                 'receiveTask', 'userTask', 'manualTask', 'businessRuleTask', 'serviceTask', 'scriptTask',
                 'callActivity', 'subProcess', 'dataObject', 'dataStoreReference', 'boundaryEvent', 'textAnnotation',
                 'collaboration', 'laneSet', 'sequenceFlow', 'group']
# Outer Elements are those that appear at child level from a process
innerElements = ['participant', 'messageFlow', 'lane', 'dataInputAssociation', 'dataOutputAssociation']
# Inner Elements are those that appear at child level from an outer element
eventDefinitions = ['messageEventDefinition', 'timerEventDefinition', 'conditionalEventDefinition',
                    'signalEventDefinition', 'linkEventDefinition', 'escalationEventDefinition',
                    'compensateEventDefinition', 'errorEventDefinition', 'terminateEventDefinition',
                    'cancelEventDefinition']
# These do not account for non-interrupting instances, so they are added on the command line below for when needed
eventDefinitions += [eventDefinitions[i] + 'NonInterrupting' for i in [0, 1, 2, 3, 5, 6, 7, 9]]
# Below, we set shorter lists for each type of element to improve on performance
startEventDefinitions = eventDefinitions[0:4]
intermediateCatchEventDefinitions = eventDefinitions[0:5]
intermediateThrowEventDefinitions = [eventDefinitions[i] for i in [0, 3, 4, 5, 6]]
endEventDefinitions = [eventDefinitions[i] for i in [0, 3, 5, 6, 7, 8]]
boundaryEventDefinitions = [eventDefinitions[i] for i in [0, 1, 2, 3, 5, 6, 7, 9]] + [eventDefinitions[i] +
                                                                                      'NonInterrupting' for i in
                                                                                      [0, 1, 2, 3, 5, 6, 7, 9]]
taskDefinitions = ['multiInstanceLoopCharacteristics', 'standardLoopCharacteristics']
multiInstanceTypes = ['multiInstanceLoopSequential', 'multiInstanceLoopParallel']
# taskDefintions and multiInstanceTypes both are to solve sequential, parallel, and loop tasks
subinfos = {'startEvent': startEventDefinitions, 'intermediateCatchEvent': intermediateCatchEventDefinitions,
            'intermediateThrowEvent': intermediateThrowEventDefinitions, 'endEvent': endEventDefinitions,
            'boundaryEvent': boundaryEventDefinitions}
# Below lists are set for both indexes and columns of the resulting dataframe, before treated
dataframe_cols = ['regular'] + eventDefinitions + multiInstanceTypes + [taskDefinitions[-1]]
dataframe_index = outerElements + innerElements + ['subProcess_' + x for x in outerElements + innerElements]
# Below was the original form of getting the .bpmn files. This has been updated since.
# paths = os.listdir(cwd)
# paths = [os.path.join(cwd, x) for x in paths if x.endswith('.bpmn')]


# Inner count of elements. Separated to be reused for subprocesses as well.
def count_elements(df, element, subprocess=False):
    inner_df = pandas.DataFrame(0, index=dataframe_index, columns=dataframe_cols)
    rawcatch = {x: [] for x in outerElements}

    # Initial count of elements, only on direct child level (to avoid subprocess overcounting elements)
    for outerElement in outerElements:
        rawcatch[outerElement] += element.find_all(outerElement, recursive=False)
    # Refinement of findings - types of elements, inner definitions.
    for k, v in rawcatch.items():
        index = k
        if subprocess:
            index = 'subProcess_' + k
        if k == 'startEvent':
            total_inners = 0
            for startEvent in v:
                for inner in startEventDefinitions:
                    result = startEvent.find(inner)
                    if result:
                        inner_df.at[index, inner] += 1
                        total_inners += 1
                for innerElement in innerElements:
                    found = startEvent.find_all(innerElement, recursive=False)
                    inner_df.at[innerElement, 'regular'] += len(found)
            inner_df.at[index, 'regular'] = len(v) - total_inners
        if k == 'intermediateCatchEvent':
            for intermediateCatchEvent in v:
                for inner in intermediateCatchEventDefinitions:
                    result = intermediateCatchEvent.find(inner)
                    if result:
                        inner_df.at[index, inner] += 1
                for innerElement in innerElements:
                    found = intermediateCatchEvent.find_all(innerElement, recursive=False)
                    inner_df.at[innerElement, 'regular'] += len(found)
        if k == 'intermediateThrowEvent':
            for intermediateThrowEvent in v:
                for inner in intermediateThrowEventDefinitions:
                    result = intermediateThrowEvent.find(inner)
                    if result:
                        inner_df.at[index, inner] += 1
                for innerElement in innerElements:
                    found = intermediateThrowEvent.find_all(innerElement, recursive=False)
                    inner_df.at[innerElement, 'regular'] += len(found)
        if k == 'endEvent':
            total_inners = 0
            for endEvent in v:
                for inner in endEventDefinitions:
                    result = endEvent.find(inner)
                    if result:
                        inner_df.at[index, inner] += 1
                        total_inners += 1
                for innerElement in innerElements:
                    found = endEvent.find_all(innerElement, recursive=False)
                    inner_df.at[innerElement, 'regular'] += len(found)
            inner_df.at[index, 'regular'] = len(v) - total_inners
        if k.endswith('task') or k.endswith('Task') or k == 'callActivity':  # grouped because of similarities
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
                for innerElement in innerElements:
                    found = task.find_all(innerElement, recursive=False)
                    inner_df.at[innerElement, 'regular'] += len(found)
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
                for innerElement in innerElements:
                    found = boundaryEvent.find(innerElement, recursive=False)
                    if found:
                        inner_df.at[innerElement, 'regular'] += len(found)
        if k == 'subProcess':
            inner_df.at[index, 'regular'] += len(v)
            for subProcess in v:  # Subprocess
                inner_df = count_elements(inner_df, subProcess, subprocess=True)
        if k.endswith('Gateway') or k == 'textAnnotation' or k == 'dataObject' or k == 'dataStoreReference':
            inner_df.at[index, 'regular'] += len(v)
            for element in v:
                for innerElement in innerElements:
                    found = element.find_all(innerElement, recursive=False)
                    inner_df.at[innerElement, 'regular'] += len(found)
        if k == 'sequenceFlow' or k == 'group':
            inner_df.at[index, 'regular'] += len(v)
        if k == 'laneSet':
            for laneSet in v:
                inner_df.at[k, 'regular'] += 1
                found = laneSet.find_all('lane', recursive=False)
                inner_df.at['lane', 'regular'] += len(found)
    # Final results of this execution are joined with previous ones sent as parameters, grouping results of subprocesses
    result_df = df + inner_df
    return result_df


def start_counts():
    # Layout set here
    gui_layout = [[psg.Text('Choose files to be counted:')],
                  [psg.InputText("", size=(70, 10), disabled=True),
                   psg.FilesBrowse(file_types=(("BPMN Files", "*.bpmn"),))],
                  [psg.Text('Chosse location for output file:')],
                  [psg.InputText("", size=(70, 10), disabled=True), psg.FolderBrowse()],
                  [psg.OK("Count elements in selected files", auto_size_button=True)]]
    window = psg.Window('BPMNCount', layout=gui_layout, disable_close=True)
    while True:  # Grants only correct execution will proceed - not one without an output target
        event, values = window.read()
        if event in (None, 'Count elements in selected files'):
            if values[1] == '':
                psg.popup_ok('Output location must be selected.')
            else:
                break
    pathways = values[0]
    output_location = values[1]
    pathways = pathways.split(';')
    print(pathways)
    final_df = pandas.DataFrame(0, index=dataframe_index, columns=dataframe_cols)
    for pathway in pathways:  # Executes for each file given
        print(pathway)
        dataframe = pandas.DataFrame(0, index=dataframe_index, columns=dataframe_cols)  # receives results for each path
        with open(pathway, 'r', encoding='utf8') as file:
            content = "".join(file.readlines())
            soup = BeautifulSoup(content, 'xml')  # 'xml' setting needed to interpret .bpmn files
            collaborations = soup.find_all('collaboration')
            processes = soup.find_all('process')  # File should have 1, however some modelers add empty processes
            for process in processes:
                dataframe = count_elements(dataframe, process)
            for collaboration in collaborations:  # Participants and messageFlows are recorded outside of processes
                for innerElement in innerElements:
                    found = collaboration.find_all(innerElement)
                    dataframe.at[innerElement, 'regular'] += len(found)
            dataframe.to_csv(os.path.join(output_location, pathway.split('/')[-1] + '.csv'))  # For manual checks
        final_df = final_df + dataframe  # Final dataframe before removing empty rows and columns
    final_df = final_df.loc[(final_df.sum(axis=1) != 0), (final_df.sum(axis=0) != 0)]  # Cleans up uneeded lack of info
    print(final_df)
    gui_exit_layout = [[psg.Text("Files have been processed, and output will be at the specified location ")],
                       [psg.Text("under the name 'count_bpmn_elements.csv'.")],
                       [psg.Text("Click 'OK' to finish execution. ")],
                       [psg.OK("OK")]]
    window = psg.Window('BPMNCount - Files processed', layout=gui_exit_layout, disable_close=True)
    event, values = window.read()
    final_df.to_csv(os.path.join(output_location, 'count_bpmn_elements.csv'))  # Final result of execution


start_counts()
