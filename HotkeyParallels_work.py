import maya.cmds as cmds # type: ignore

# Hotkey Parallels
# Maya 2024 | 1.0.1b
# Julien Rogar ( https://github.com/JulienRogar/HotkeyParallels )

#--- ---

#region - Functions
def clearUI(): #Clear file columns and action column's children
    elements = cmds.rowLayout( BuildWindow.elementsLayout, query=True, childArray=True )
    elements.pop(0)
    elementsCount = len(elements)
    #Files
    if elements != None and elementsCount != 0: #Check if the scroll area doesn't have only the actions layout
        cmds.deleteUI(elements)
    #Actions
    actions = cmds.columnLayout( BuildWindow.actionsLayout, query=True, childArray=True )
    if actions != None:
        cmds.deleteUI(actions)
# Main UI
def buildUI_TopIcon( image='', height=30, width=30, parent='', command='', annotation='', dropCallback=None ): #Build symbolButton icons for the top bar
    if command!='':
        if dropCallback==None: #Command
            cmds.symbolButton(
                annotation=annotation,
                command=command,
                height=height, width=width,
                image=image,
                parent=parent
            )
        else: #Command and dropCallback
            cmds.symbolButton(
                annotation=annotation,
                command=command,
                dropCallback=dropCallback,
                height=height, width=width,
                image=image,
                parent=parent
            )
    elif dropCallback!=None: #DropCallback
        cmds.symbolButton(
            annotation=annotation,
            dropCallback=dropCallback,
            height=height, width=width,
            image=image,
            parent=parent
        )
    else: #None
        cmds.symbolButton(
            annotation=annotation,
            height=height, width=width,
            image=image,
            parent=parent
        )

def buildUI_ScrollArea(rebuild=False): #Build the scroll area
    if rebuild:
        cmds.deleteUI(BuildWindow.scrollAreaLayout)
    scrollLyt = cmds.scrollLayout(
        height=188,
        borderVisible=False,
        childResizable=False,
        panEnabled=True,
        resizeCommand='updateUI_ScrollArea()',
        backgroundColor=ThemeColor.scrllArea,
        parent=BuildWindow.mainLyt
    )
    BuildWindow.scrollAreaLayout = scrollLyt
    info_subLyt = cmds.rowLayout(
        height=636, width=1246,
        numberOfColumns=ParallelsCore.files_columnsCount
    )
    BuildWindow.elementsLayout = info_subLyt
    
    BuildWindow.actionsLayout = cmds.columnLayout(
        height=630, width=240,
        backgroundColor=ThemeColor.acColumn,
        parent=info_subLyt
    )

    t_topLyt = BuildWindow.topLyt
    cmds.formLayout( #Update the form layout to manage the size of the top and scroll layouts' size
        BuildWindow.mainLyt, edit=True,
        attachForm=(
            (t_topLyt, 'top', 15), (t_topLyt, 'left', 15), (t_topLyt, 'right', 15),
            (scrollLyt, 'left', 15), (scrollLyt, 'right', 15), (scrollLyt, 'bottom', 15)
        ),
        attachControl=(
            (scrollLyt, 'top', 10, t_topLyt)
        )
    )

def buildUI_ActionsFiles(progress=False): #Build actions' and files' UIs and update scroll area
    #Build actions column UI
    if progress:
        ProgressWindow.update('Building UI: actions...',1,None,'',True)
    buildUI_Actions( ParallelsCore.files_actions, 238, BuildWindow.actionsLayout )
    #Build file column UI for each file
    fileIndex=0
    filesIdxCount=ParallelsCore.files_filesCount
    for file in ParallelsCore.files_idx: #For among the idx list to have index 0 be main file
        if progress:
            ProgressWindow.update('Building UI: File',fileIndex-1,filesIdxCount)
        data = ParallelsCore.files_HKData.get(file)
        buildUI_File(f'{file}',data,218,BuildWindow.elementsLayout,fileIndex)
        fileIndex+=1
    if progress:
        ProgressWindow.update('Building UI: matching scroll area...',1,None,'',True)
    updateUI_ScrollArea()

def buildUI_Actions( actions=[], width=10, parent=None): #Build action(s) on the actions column
    cmds.separator( height=46, width=width, style='none', parent=parent ) #Empty area
    doRmvHide = True if BuildWindow.hideRemoved else False
    actionInfo = 'INFO:  Hotkey\n\n[ Runtime command ]  '
    actionRmvInfo = 'INFO:  HKP_Removed_( found hotkey data )  '
    rtmCmds = ParallelsCore.files_rtmCmds
    rtmCmd = None
    isRmv = None
    index=0
    for action in actions:
        isRmv = True if action.count('HKP_Removed_')==1 else False
        if doRmvHide and isRmv: #If should hide Removed and the actions is one, skip it
            continue
        cmds.separator( height=19, width=width, style='none', parent=parent )
        cmds.separator( height=2, width=width, style='none', backgroundColor=ThemeColor.acSeprator, parent=parent )
        cmds.separator( height=5, width=width, style='none', parent=parent )
        cmds.text( #Action
            label=f'<font size=4><font color={ThemeColor.txt_light}>{action}</font>', annotation=actionRmvInfo if isRmv else actionInfo,
            height=49, width=width,
            align='center', font='boldLabelFont', recomputeSize=False, wordWrap=True,
            parent=parent
        )
        if isRmv:
            cmds.separator( height=49, width=width, style='none', parent=parent )
        else: #If not Removed, should have a runtime command
            rtmCmd = rtmCmds[index]
            cmds.text( #Runtime command
                label=f'<font size=4><font color={ThemeColor.txt_keyRtmCmd}>[ {rtmCmd} ]</font>', annotation=actionInfo,
                height=49, width=width,
                align='center', font='obliqueLabelFont', recomputeSize=False, wordWrap=True,
                parent=parent
            )
        index+=1

def buildUI_File( label='File', data={}, width=10, parent=None, fileIndex=-1 ): #Build file column
    fileLyt = cmds.columnLayout(
        height=630, width=240,
        columnAlign='center',
        margins=10,
        backgroundColor=ThemeColor.fileColumn,
        parent=parent
    )
    #File title
    cmds.text(
        label=f'<font size=4><font color={ThemeColor.txt_light}>{label}</font>',
        align='center',
        font='boldLabelFont',
        height=31,
        width=width,
        dragCallback="None", #No action to do but will be draggeable
        backgroundColor=ThemeColor.fileName,
        parent=fileLyt
    )
    cmds.separator( height=13, width=width, style='none', parent=fileLyt )
    #Keys
    keyWidth = width+4
    actions = ParallelsCore.files_actions
    isMain = True if fileIndex==0 else False
    doRmvHide = True if BuildWindow.hideRemoved else False
    mainFileData = ParallelsCore.files_HKData[ParallelsCore.files_idx[0]]

    for action in actions: #actions is in the order so use it to generate keys in matching order
        if doRmvHide and action.count('HKP_Removed_'): #If should hide Removed and the actions is one, skip it
            continue
        
        fullKey = get_HotkeyData(action, data)
        status = compare_MainFileKey(action,fullKey[0],fileIndex,fullKey[1],mainFileData) #Find the status of the action for this file index
        if fullKey[1]: #If data has been found for it, extract and compare it then build UI
            keyData = fullKey[2]
            keyDataExtra = keyData[1]
            buildUI_Key( keyWidth, fileLyt, keyData[0], keyDataExtra[0], keyDataExtra[1], keyDataExtra[2], keyDataExtra[3], status, isMain )
        else: #If didn't found data for it, compare and build UI
            buildUI_Key( keyWidth, fileLyt, '', False, False, False, False, status, isMain )

def get_HotkeyData(action='', data={}, returnShort=False): #Extract info from an action in data dictionnary and returns with to compare or with all useful infos to also build UI
    action = f'{action}_HKData'
    kData = data.get(action)
    fKeyExtra = ''
    hasData = False
    keySplit = []
    if kData!=None: #If has data found
        hasData = True
        k_Shortcut = kData[1].title()
        k_Mods = kData[2]
        k_Extra = kData[3]
        fKey = f"{'Ctrl+' if k_Mods[0] else ''}{'Shift+' if k_Mods[1] else ''}{'Alt+' if k_Mods[2] else ''}{k_Shortcut}" #Shortcut
        fKeyExtra = f"{fKey}{'1' if k_Extra[0] else '0'}{'1' if k_Extra[1] else '0'}{'1' if k_Extra[2] else '0'}{'1' if k_Extra[3] else '0'}" #Shortcut and extra infos, to compare
        keySplit = [ fKey, k_Extra ]
    else: #No data found
        fKey = ''
    
    if returnShort: #Only returns the full key with extra to be compared
        return fKeyExtra
    else: #Returns every useful info, full key to compare, if has data and detailled key parts
        total = [ fKeyExtra, hasData, keySplit ]
        return total

def compare_MainFileKey( action=None, key='', fileIndex=-1, hasHKData=False, mainFileData={} ): #Determine status of a file's key
    status=-1
    if fileIndex==0: #Main file
        if key == '': #Key empty
            if hasHKData: #Likely removed and no key for some reason
                status=4 #Removed
            else: #Action not existing at all in the file
                status=5 #Not existing
        else: #Key not empty
            if action.count('HKP_Removed_')==1:
                status=4 #Removed
            else:
                status=0
    else: #Compare to main file
        if key == '': #Key empty
            if ParallelsCore.files_actionsMainFile.count(action) == 1: #If action is among the main file actions
                if action.count('HKP_Removed_')==1 and hasHKData:
                    status=4 #Removed
                else:
                    status=3 #Missing
            else: #Action not existing at all in the file and main file
                status=5 #Not existing
        else: #Key not empty
            if action.count('HKP_Removed_')==1:
                status=4 #Removed
            else:
                kMainFile = get_HotkeyData( action, mainFileData, True )
                actionDataName = f'{action}_HKData'
                if actionDataName in mainFileData:
                    if kMainFile == key:
                        status=0 #Normal
                    else:
                        status=1 #Different
                else:
                    status=2 #Added
    return status

def buildUI_Key( width=10, parent=None, key='Key', onPress=False, onRelease=False, repeatable=False, customScript=False, status=-1, isMain=False ): #Build key UI that will be child of it's file column
    cmds.separator( height=12, width=width, style='none', parent=parent )
    cmds.separator( height=2, width=width, style='none', backgroundColor=ThemeColor.fileSeparator, parent=parent )
    cmds.separator( height=8, width=width, style='none', parent=parent )
    #Layout
    statusBack_Bool = True if status!=0 else False
    statusBack_Color = ThemeColor.unknown #Defaults to unknown
    statusInfo = ''
    cstmDisplay = False
    statusIcon = ''
    if status!=0: #Update statusBack_Color, statusInfo and eventually cstmDisplay according to the status
        if status==1:
            statusBack_Color = ThemeColor.alternate
            statusInfo = 'INFO: [Alternate] Key different from the main file'
            statusIcon = 'projectCurveSplit_Poly.png'
        elif status==2:
            statusBack_Color = ThemeColor.added
            statusInfo = 'INFO: [Added] Key added compared to the main file'
            statusIcon = 'Bool_BMinusA.png'
        elif status==3:
            statusBack_Color = ThemeColor.missing
            statusInfo = 'INFO: [Missing] Action not existing on this file compared to the main file'
            cstmDisplay = True
        elif status==4:
            statusBack_Color = ThemeColor.removed
            statusInfo = 'INFO: [Removed] Default Maya key that has likely been unassigned'
            cstmDisplay = True
        elif status==5:
            statusBack_Color = ThemeColor.notExisting
            statusInfo = 'INFO: [Not existing] Action not existing on the main file' if isMain else 'INFO: [Not existing] Action not existing on the main file and this file'
            cstmDisplay = True
        elif status<0 or status>5:
            statusInfo = 'INFO: [Unknown] Unknown status for the key. Something must have went wrong on the HotkeyParallels'
            statusIcon = 'info.png'

    borderLyt = cmds.columnLayout(
        height=102,width=width,
        adjustableColumn=False,
        margins=2,
        backgroundColor=statusBack_Color, enableBackground=statusBack_Bool, annotation=statusInfo,
        parent=parent
    )
    clmnLyt = cmds.columnLayout(
        height=98,width=(width-4),
        adjustableColumn=False,
        rowSpacing=10,
        margins=5,
        columnOffset=('left', 5),
        backgroundColor=ThemeColor.keyBack,
        parent=borderLyt
    )
    if cstmDisplay: #Key UI only contains specific status display
        if status==3:
            cmds.text(
                label=f'<font color={ThemeColor.txt_missing}><font size=5>Missing</font>',
                height=96, width=(width-4)-20,
                align='center', hyperlink=False, recomputeSize=False, wordWrap=False, font='obliqueLabelFont',
                parent=clmnLyt
            )
        elif status==4:
            cmds.text(
                label=f'<font color={ThemeColor.txt_removed}><font size=5>Removed</font>',
                height=96, width=(width-4)-20,
                align='center', hyperlink=False, recomputeSize=False, wordWrap=False, font='obliqueLabelFont',
                parent=clmnLyt
            )
        elif status==5:
            cmds.text(
                label=f'<font color={ThemeColor.txt_none}><font size=5>None</font>',
                height=96, width=(width-4)-20,
                align='center', hyperlink=False, recomputeSize=False, wordWrap=False, font='obliqueLabelFont',
                parent=clmnLyt
            )
            cmds.columnLayout( clmnLyt, edit=True, backgroundColor=statusBack_Color )
    else : #Classic display with key, eventually status icon and key extra
        #Row top
        topLyt = cmds.flowLayout(
            height=35, width=width,
            columnSpacing=10,
            wrap=False,
            parent=clmnLyt
        )
        keyCount = key.count('') #Choose key text's size according to how long it is
        fontSize = 4
        if keyCount<23:
            fontSize=4
        elif keyCount<27:
            fontSize=3
        else:
            fontSize=2
        cmds.text( #Key
            label=f'<font size={fontSize}><font color={ThemeColor.txt_key}>{key}</font>', annotation=f'INFO: Key [ {key} ]',
            height=35, width=153,
            align='center', hyperlink=False, recomputeSize=False, wordWrap=False,
            parent=topLyt,
            backgroundColor=ThemeColor.keyInfo
        )
        if statusBack_Bool: #Status icon
            cmds.symbolButton(
                height=35, width=35,
                image=statusIcon,
                parent=topLyt,
                backgroundColor=statusBack_Color,
                annotation=statusInfo
            )
        else:
            cmds.separator(
                height=35, width=35,
                style='none',
                parent=topLyt
            )

        #Row bottom
        extraWidth = (width/2)-10
        botLyt = cmds.gridLayout(
            height=40, width=(width-20),
            allowEmptyCells=False, autoGrow=False, columnsResizable=False,
            cellWidthHeight=(extraWidth,20),
            numberOfRowsColumns=(2,2),
            parent=clmnLyt,
            backgroundColor=ThemeColor.keyInfo,
            annotation=f'INFO: Parameters [ On press: {str(onPress).upper()} - On release: {str(onRelease).upper()} - Repeatable: {str(repeatable).upper()} - Custom script: {str(customScript).upper()} ]'
        )
        buildUI_KeyExtra('⎡⎡ On press', onPress, extraWidth, botLyt)
        buildUI_KeyExtra('Repeatable', repeatable, extraWidth, botLyt)
        buildUI_KeyExtra('⎣⎣ On release', onRelease, extraWidth, botLyt)
        buildUI_KeyExtra('Custom script', customScript, extraWidth, botLyt)

def buildUI_KeyExtra( label='', value=False, width=20, parent=None ): #Create checkbox for a key UI's key extra
    if ThemeColor.keyChkBxBack==None:
        cmds.checkBox(
            label=label, value=value,
            height=20, width=width,
            editable=False, recomputeSize=False,
            parent=parent
        )
    else: #With an invisible background that will still be visible on the checkbox's background color and change the text's color
        cmds.checkBox(
            label=label, value=value,
            height=20, width=width,
            editable=False, recomputeSize=False,
            backgroundColor=ThemeColor.keyChkBxBack, enableBackground=False,
            parent=parent
        )

def updateUI_ScrollArea(): #Update the size of the scroll area UI to match the children or the minimum default size
    #Height
    actionsAmount = len(ParallelsCore.files_actions)-ParallelsCore.files_removedCount if BuildWindow.hideRemoved else len(ParallelsCore.files_actions) #Do not count the removed_ actions if they are hidden
    scrllH = cmds.scrollLayout( BuildWindow.scrollAreaLayout, query=True, height=True )
    elementHeight=None
    if actionsAmount > 4: #4 is because of window's default size, if higher just count the scrollArea's height with margins + height added by actions + difference between the default scrollArea height once updated by above formLayout and current scrollArea height
        elementHeight = int( (scrllH-6) + ((actionsAmount-4.55) * 124) + (640-scrllH) ) #12+2+8+102 -> 124
    elif actionsAmount >= 1: #If still actions, the height for one action + the height added by each action after the first
        elementHeight = int( 188 + ((actionsAmount-1 if actionsAmount>1 else 0) * 124) ) #20+31+13+12+2+8+102 -> 188 ; #12+2+8+102 -> 124
    else: #Just the height of the scrollArea minus the margins
        elementHeight = (scrllH-6)

    #Width
    fileCount = ParallelsCore.files_filesCount
    elementWidth = 243 + (240 * (fileCount if fileCount > 0 else 1)) + (2*fileCount) #240 (action column width) + 3 (minimum margins with action and one file column) -> 243 ; +2 as margin for each file
    
    #Set height for children columns before so when window size gets increased there is no quick vertical adjustement of them in the parent before they get their size updated
    children = cmds.rowLayout( BuildWindow.elementsLayout, query=True, childArray=True )
    for child in children:
        cmds.columnLayout( child, edit=True, height=elementHeight )
    #cmds.rowLayout( BuildWindow.elementsLayout, edit=True, height=elementHeight, width=elementWidth )
    cmds.rowLayout( BuildWindow.elementsLayout, edit=True, height=elementHeight, width=elementWidth )
    
    #Set scrollLayout's size to the minimum size for when there is one action and one file, Maya will directly get the parent formLayout to resize the scrollLayout but it should keep this as the minimum size for the window's resizing
    minHeight=194
    minWidth=489
    if fileCount>1: #More columns than minimum size
        minHeight=206 #+12 to include the horizontal scrollBar
    if BuildWindow.hideRemoved and actionsAmount-ParallelsCore.files_removedCount>1 or actionsAmount>1: #Hide Removed and more than one non-Removed action or don't hide Removed and more than one action
        minWidth=501 #+12 to include the vertical scrollBar
    cmds.scrollLayout( BuildWindow.scrollAreaLayout, edit=True, height=minHeight, width=minWidth )

def buildUI_RefreshUIConfirm(): #Stop scroll layout and put a UI to confirm refresh (Direct refresh called even indirectly from a UI control in UI that will be deleted would cause a Maya crash)
    if BuildWindow.refreshLayout != None:
        return
    cmds.rowLayout( BuildWindow.elementsLayout, edit=True, manage=False ) #When 5 or more files are imported directly, Maya keeps scrollLayout and actionLayout visible for some reason so directly unmanage the elementsLayout
    cmds.scrollLayout( BuildWindow.scrollAreaLayout, edit=True, backgroundColor=ThemeColor.mainArea ) #And make the scrollLayout's background color same as mainArea's
    rfrshH = 300
    scrllH = cmds.scrollLayout( BuildWindow.scrollAreaLayout, query=True, height=True )-2
    if scrllH < rfrshH: #If window is sized in a way scrollLayout's height is smaller than the aimed height for the refresh confirmation layout
        rfrshH = scrllH #Set the refresh confirmation's height same as scrollLayout's so the window doesn't get sized up by the confirmation UI
    refreshLayout = cmds.columnLayout(
        height=rfrshH,
        adjustableColumn=True,
        parent=BuildWindow.mainLyt
    )
    BuildWindow.refreshLayout = refreshLayout
    cmds.text(
        label=f'<font size=6><font color={ThemeColor.txt_light}>Refresh</font>',
        height=50,
        recomputeSize=False,
        parent=refreshLayout
    )
    cmds.symbolButton(
        image='refresh.png',
        height=rfrshH-50,
        command='refreshUI()',
        enableKeyboardFocus=True,
        backgroundColor=ThemeColor.Bttn,
        parent=refreshLayout
    )
    cmds.formLayout(
        BuildWindow.mainLyt, edit=True,
        attachForm=(
            (refreshLayout, 'left', 15), (refreshLayout, 'right', 15), (refreshLayout, 'bottom', 15)
        ),
        attachControl=(
            (refreshLayout, 'top', 10, BuildWindow.topLyt)
        )
    )

def refreshUICheck(): #Check if there is a refreshLayout and manage action cumul. If no cumul returns False, if cumul allowed returns True
    if BuildWindow.refreshLayout!=None and BuildWindow.refreshMltAllowed==False:
        if BuildWindow.refreshMltAsked==False:
            cmds.warning('INFO: You are already waiting the refresh of a previous action. Please click again if you want to cumulate this and next actions before refresh')
            BuildWindow.refreshMltAsked=True
            return False
        else:
            BuildWindow.refreshMltAllowed=True
            BuildWindow.refreshMltCount=1
            cmds.warning('INFO: This action will cumulate before refresh')
    elif BuildWindow.refreshMltAllowed:
        BuildWindow.refreshMltCount+=1
        cmds.warning(f'INFO: This action will cumulate before refresh ({BuildWindow.refreshMltCount})')
    return True

def clearUI_RefreshUIConfirm(): #Remove the refresh confirm UI and reset confirmation variables
    if BuildWindow.refreshLayout != None: #Remove refresh confirm UI
        cmds.deleteUI(BuildWindow.refreshLayout)
        BuildWindow.refreshLayout=None
    BuildWindow.refreshMltAsked=False
    BuildWindow.refreshMltAllowed=False
    BuildWindow.refreshMltCount=0

def refreshUI(): #Remove refresh confirm layout, get scroll area back, rebuild it if asked or clear it and call action(s)' and file(s)' UIs' build
    clearUI_RefreshUIConfirm()
    cmds.rowLayout( BuildWindow.elementsLayout, edit=True, manage=True )
    cmds.scrollLayout( BuildWindow.scrollAreaLayout, edit=True, backgroundColor=ThemeColor.scrllArea )
    if BuildWindow.refreshWaitRebuild: #If was stored the ask to rebuild scroll layout, call a scroll layout rebuild and reset the stored ask to rebuild variable
        buildUI_ScrollArea(True)
        BuildWindow.refreshWaitRebuild=False
    else: #Just clear the actions and files UIs
        clearUI()
    buildUI_ActionsFiles() #Rebuild action(s)' and file(s)' UIs
# Top buttons
def bttn_TopPress(resultType:int): #0 Remove / 1 Set main file / 2 reorder left / 3 reorder right. To be called by the top buttons when clicked
    idx = BuildWindow.intFieldIdx-1 #-1 because arrays start by 0, the one in intField starts with 1 for user comfort
    if idx==-1:
        cmds.warning( 'File index set to 0 on the input field. It needs to be at least 1 to have an effect on a file', n=True )
        return
    if idx > ParallelsCore.files_filesCount:
        cmds.warning( f'The file index from the input field ({idx+1}) is bigger than the stored indexes of files ({len(ParallelsCore.files_idx)} - cached: {ParallelsCore.files_filesCount}). Did you made the impossible ?', n=True )
        return
    fileName = ParallelsCore.files_idx[idx] #Get file name according to the index
    rfrshCheck = refreshUICheck()
    if rfrshCheck==False:
        return
    if resultType==0: #Call the function according to the parameter
        apply_Remove(fileName)
    elif resultType==1:
        ParallelsCore.setAsMainFile(fileName)
    elif resultType==2:
        apply_Reorder(fileName, idx, True)
    elif resultType==3:
        apply_Reorder(fileName, idx, False)

def dragCtrlToLabel(dragControl=None): #Get label from a Maya text control output as dragControl
    dropLabel = cmds.text(dragControl, query=True, label=True) #Get label from the Maya text control
    dropLabel = dropLabel.split('>')[2] #Remove the two first font tags
    dropLabel = dropLabel.split('<')[0] #Remove the end font tag
    return dropLabel

def dropCallback_Remove(dragControl=''): #To be called when dropping over remove file button
    dropLabel = dragCtrlToLabel(dragControl)
    apply_Remove(dropLabel)

def apply_Remove(fileName=''): #Apply file remove and call a refresh confirmation
    doRebuild = ParallelsCore.removeFile(fileName)
    if doRebuild: #Use BuildWindow variable to keep the state True for refreshUI() called by buildUI_RefreshUIConfirm()
        BuildWindow.refreshWaitRebuild=True
    buildUI_RefreshUIConfirm()

def dropCallback_SetMainFile(dragControl=''): #To be called when dropping over set main file button
    dropLabel = dragCtrlToLabel(dragControl)
    ParallelsCore.setAsMainFile(dropLabel)

def dropCallback_Reorder(left:bool, dragControl=''): #To be called when dropping over left/right reorder file button
    fileName = dragCtrlToLabel(dragControl) #Get file name from the drag control
    idx = ParallelsCore.files_idx.index(fileName)
    apply_Reorder(fileName, idx, left)

def apply_Reorder(fileName=None, idx=None, left=None): #Apply file reorder and call a refresh confirmation
    if idx == 0: #Main file
        if left: #Cancel attemp to move the main file more at left
            return
        elif ParallelsCore.files_filesCount > 1: #If more than one file, directly call a set as main file for the file at right that will become the main file
            fileName = ParallelsCore.files_idx[1]
            ParallelsCore.setAsMainFile(fileName,False)
            if BuildWindow.intFieldLock: #If asked, update intField value to match
                tIdx = (idx-1 if left else idx+1)+1
                updateIntField(tIdx)
            return
        else:
            return
    if idx == 1 and left:
        ParallelsCore.setAsMainFile(fileName) #Directly call a set as main file
        return
    idxList = ParallelsCore.files_idx.copy() #Make a copy of the list that will be quicker to edit multiple times locally
    if idx==(len(idxList)-1) and left==False: #Cancel attemps to move the last file more at right
        return
    idxList.pop(idx) #Remove then replace the file name at the correct index
    fIdx = idx-1 if left else idx+1
    idxList.insert(fIdx, fileName)
    ParallelsCore.files_idx = idxList #Update actual list
    if BuildWindow.intFieldLock: #If asked, update intField value to match
        updateIntField(fIdx+1)
    buildUI_RefreshUIConfirm()

def bttn_setIntFieldIDX(): #To be called when changing the int field
    idx = cmds.intField( BuildWindow.intFieldCtrl, query=True, value=True ) #Get index from the UI
    change = False
    listLen = ParallelsCore.files_filesCount
    if listLen >= 2 and idx <= listLen: #If more than two files and index under the number of files, store it without issue
        change=True
    elif listLen <= 1: #If number of files under two, check if bigger than number of files and if so set it at the maximum number of files instead
        if idx > listLen: #This is because the intField needs two between it's min and max with a step of one, allowing to set higher index than files when there is zero or one file
            idx=listLen
            cmds.intField( BuildWindow.intFieldCtrl, edit=True, value=idx )
            change=True
        elif idx <= listLen:
            change=True
    
    if change:
        BuildWindow.intFieldIdx = idx

def bttn_setIntFieldValue(increase=True): #To be called by the increase and decrease file index buttons
    newValue = BuildWindow.intFieldIdx+1 if increase else BuildWindow.intFieldIdx-1
    if newValue < 0 or newValue > ParallelsCore.files_filesCount: #If trying to go under zero or over the number of files, cancel since the fitting value at min or max should already have been applied
        return
    cmds.intField( BuildWindow.intFieldCtrl, edit=True, value=newValue )
    bttn_setIntFieldIDX()

def setIntFieldLock(lock=False): #To be called by the file index lock button
    BuildWindow.intFieldLock=lock

def updateIntField(value=0): #To set directly the file index value without necessary check
    cmds.intField( BuildWindow.intFieldCtrl, edit=True, value=value )
    BuildWindow.intFieldIdx=value

def buildUI_SetTheme(): #To be called by the set theme icon
    newTheme = cmds.confirmDialog( #UI for the themes choice
        title='HOTKEY PARALLELS', message=f'Change window theme\n\n(This can take few seconds if there are a lot of keys)', messageAlign='center',
        button=['Very dark','Dark','Gray','Light','Cancel'],
        defaultButton='Cancel',
        parent=BuildWindow.windowName
    )
    themeChanged=False
    if newTheme=='Dark':
        ThemeColor.setTheme('dark')
        themeChanged=True
    elif newTheme=='Light':
        ThemeColor.setTheme('light')
        themeChanged=True
    elif newTheme=='Very dark':
        ThemeColor.setTheme('darker')
        themeChanged=True
    elif newTheme=='Gray':
        ThemeColor.setTheme('gray')
        themeChanged=True
    
    if themeChanged: #If new theme applied, rebuild the window
        ThemeColor.winWH = cmds.window( BuildWindow.windowName, query=True, widthHeight=True ) #Store the window's size as new size the window will be rebuilt with
        if BuildWindow.refreshLayout!=None:
            clearUI_RefreshUIConfirm()
        intMemory = [ BuildWindow.intFieldMax, BuildWindow.intFieldIdx, BuildWindow.intFieldLock ]
        scriptWindow = BuildWindow() #Redo the build but I see no need to replace with a new class object via __new__
        cmds.intField( BuildWindow.intFieldCtrl, edit=True, maxValue=intMemory[0], value=intMemory[1] )
        if intMemory[2]:
            cmds.symbolCheckBox( BuildWindow.intFieldLockCtrl, edit=True, value=True )
            BuildWindow.intFieldLock=True #Should do automatically but in case it doesn't
        buildUI_ActionsFiles() #Rebuid actions' and files' UIs
#endregion - Functions

#--- ---

class ThemeColor():
    winWH=(1280,750)
    currentTheme = None
    winBack = None
    mainArea = None
    topSeparator = None
    idxFieldBack = None
    topIDXArrwBack = None
    scrllAreaBack = None
    scrllArea = None
    acColumn = None
    acSeprator = None
    fileColumn = None
    fileSeparator = None
    fileName = None
    keyBack = None
    keyInfo = None
    keyChkBxBack = None
    hLBack = None
    Bttn = None
    txt_light = None
    txt_key = None
    txt_keyRtmCmd = None
    #Action variants
    alternate = None
    added = None
    missing = None
    removed = None
    notExisting = None
    unknown = None
    txt_missing = None
    txt_removed = None
    txt_none = None

    #Themes
    themes={
        'dark':{
            'winBack':[0.1,0.1,0.1],
            'mainArea':[0.2,0.2,0.2],
            'topSeparator':[0.14,0.14,0.14],
            'idxFieldBack':[0.24,0.24,0.24],
            'topIDXArrwBack':None,
            'scrllAreaBack':[0.15,0.15,0.15],
            'scrllArea':[0.17,0.17,0.17],
            'acColumn':[0.26,0.26,0.26],
            'acSeprator':[0.19,0.19,0.19],
            'fileColumn':[0.23,0.23,0.23],
            'fileSeparator':[0.15,0.15,0.15],
            'fileName':[0.3,0.3,0.3],
            'keyBack':[0.3,0.3,0.3],
            'keyInfo':[0.4,0.4,0.4],
            'keyChkBxBack':None,
            'hLBack':[0.3,0.3,0.3],
            'Bttn':[0.3,0.3,0.3],
            'txt_light':'lightgray',
            'txt_key':'white',
            'txt_keyRtmCmd':'darkgray',
            'alternate':[0.8,0.56,0],
            'added':[0,0.7,0.8],
            'missing':[0.6,0,0.08],
            'removed':[0.4,0.4,0.4],
            'notExisting':[0.2,0.2,0.2],
            'unknown':[0.4,0,0.7],
            'txt_missing':'firebrick',
            'txt_removed':'gray',
            'txt_none':'gray'
        },
        'light':{
            'winBack':[1,1,1],
            'mainArea':[0.9,0.9,0.9],
            'topSeparator':[0.4,0.4,0.4],
            'idxFieldBack':[0.86,0.86,0.86],
            'topIDXArrwBack':None,
            'scrllAreaBack':[0.9,0.9,0.9],
            'scrllArea':[0.95,0.95,0.95],
            'acColumn':[0.88,0.88,0.88],
            'acSeprator':[0.77,0.77,0.77],
            'fileColumn':[0.9,0.9,0.9],
            'fileSeparator':[0.78,0.78,0.78],
            'fileName':[0.95,0.95,0.95],
            'keyBack':[0.95,0.95,0.95],
            'keyInfo':[0.9,0.9,0.9],
            'keyChkBxBack':None,
            'hLBack':[0.95,0.95,0.95],
            'Bttn':[0.77,0.77,0.77],
            'txt_light':'gray',
            'txt_key':'dimgray',
            'txt_keyRtmCmd':'gray',
            'alternate':[0.8,0.56,0],
            'added':[0,0.7,0.8],
            'missing':[0.6,0,0.08],
            'removed':[0.4,0.4,0.4],
            'notExisting':[0.85,0.85,0.85],
            'unknown':[0.4,0,0.7],
            'txt_missing':'firebrick',
            'txt_removed':'gray',
            'txt_none':'gray'
        },
        'darker':{
            'winBack':[0,0,0],
            'mainArea':[0.13,0.13,0.13],
            'topSeparator':[0.23,0.23,0.23],
            'idxFieldBack':[0.18,0.18,0.18],
            'topIDXArrwBack':None,
            'scrllAreaBack':[0,0,0],
            'scrllArea':[0.1,0.1,0.1],
            'acColumn':[0.15,0.15,0.15],
            'acSeprator':[0.19,0.19,0.19],
            'fileColumn':[0.14,0.14,0.14],
            'fileSeparator':[0.2,0.2,0.2],
            'fileName':[0.11,0.11,0.11],
            'keyBack':[0.12,0.12,0.12],
            'keyInfo':[0.21,0.21,0.21],
            'keyChkBxBack':[1,1,1],
            'hLBack':[0.12,0.12,0.12],
            'Bttn':[0.22,0.22,0.22],
            'txt_light':'silver',
            'txt_key':'lightgray',
            'txt_keyRtmCmd':'darkgray',
            'alternate':[0.64,0.448,0],
            'added':[0,0.56,0.64],
            'missing':[0.42,0,0.056],
            'removed':[0.2,0.2,0.2],
            'notExisting':[0.1,0.1,0.1],
            'unknown':[0.28,0,0.49],
            'txt_missing':'darkred',
            'txt_removed':'darkgray',
            'txt_none':'dimgray'
        },
        'gray':{
            'winBack':[0.5,0.5,0.5],
            'mainArea':[0.5,0.5,0.5],
            'topSeparator':[0.2,0.2,0.2],
            'idxFieldBack':[0.55,0.55,0.55],
            'topIDXArrwBack':[0.55,0.55,0.55],
            'scrllAreaBack':[0.6,0.6,0.6],
            'scrllArea':[0.65,0.65,0.65],
            'acColumn':[0.55,0.55,0.55],
            'acSeprator':[0.77,0.77,0.77],
            'fileColumn':[0.4,0.4,0.4],
            'fileSeparator':[0.2,0.2,0.2],
            'fileName':[0.55,0.55,0.55],
            'keyBack':[0.5,0.5,0.5],
            'keyInfo':[0.58,0.58,0.58],
            'keyChkBxBack':None,
            'hLBack':[0.4,0.4,0.4],
            'Bttn':[0.35,0.35,0.35],
            'txt_light':'dark',
            'txt_key':'dark',
            'txt_keyRtmCmd':'dark',
            'alternate':[0.8,0.56,0],
            'added':[0,0.7,0.8],
            'missing':[0.6,0,0.08],
            'removed':[0.3,0.3,0.3],
            'notExisting':[0.36,0.36,0.36],
            'unknown':[0.4,0,0.7],
            'txt_missing':'darkred',
            'txt_removed':'dark',
            'txt_none':'dark'
        }
    }

    def setTheme(themeName): #Apply theme according to theme name
        theme=ThemeColor.themes[themeName]
        ThemeColor.currentTheme = themeName
        ThemeColor.winBack = theme['winBack']
        ThemeColor.mainArea = theme['mainArea']
        ThemeColor.topSeparator = theme['topSeparator']
        ThemeColor.idxFieldBack = theme['idxFieldBack']
        ThemeColor.topIDXArrwBack = theme['topIDXArrwBack']
        ThemeColor.scrllAreaBack = theme['scrllAreaBack']
        ThemeColor.scrllArea = theme['scrllArea']
        ThemeColor.acColumn = theme['acColumn']
        ThemeColor.acSeprator = theme['acSeprator']
        ThemeColor.fileColumn = theme['fileColumn']
        ThemeColor.fileSeparator = theme['fileSeparator']
        ThemeColor.fileName = theme['fileName']
        ThemeColor.keyBack = theme['keyBack']
        ThemeColor.keyInfo = theme['keyInfo']
        ThemeColor.keyChkBxBack = theme['keyChkBxBack']
        ThemeColor.hLBack = theme['hLBack']
        ThemeColor.Bttn = theme['Bttn']
        ThemeColor.txt_light = theme['txt_light']
        ThemeColor.txt_key = theme['txt_key']
        ThemeColor.txt_keyRtmCmd = theme['txt_keyRtmCmd']
        ThemeColor.alternate = theme['alternate']
        ThemeColor.added = theme['added']
        ThemeColor.missing = theme['missing']
        ThemeColor.removed = theme['removed']
        ThemeColor.notExisting = theme['notExisting']
        ThemeColor.unknown = theme['unknown']
        ThemeColor.txt_missing = theme['txt_missing']
        ThemeColor.txt_removed = theme['txt_removed']
        ThemeColor.txt_none = theme['txt_none']

class ProgressWindow():
    show=True
    inProgress=False
    progressMax=-1
    keepWindow=False
    
    def buildUI(status,maxCount,keepWindow): #Build progress window
        if ProgressWindow.show==False or ProgressWindow.inProgress:
            return
        
        ProgressWindow.inProgress=True
        ProgressWindow.progressMax=maxCount
        status=ProgressWindow.fixStatus(status,maxCount)
        cmds.progressWindow(
            title='HOTKEY PARALLELS',
            status=f"{status} 0/{maxCount}", progress=maxCount, maxValue=maxCount,
            isInterruptable=False
        )
        ProgressWindow.keepWindow=keepWindow

        while ProgressWindow.inProgress: #Check in loop if progress is done
            if cmds.progressWindow( query=True, isCancelled=True ):
                ProgressWindow.inProgress=False
                break
            if cmds.progressWindow( query=True, progress=True ) >= ProgressWindow.progressMax:
                ProgressWindow.inProgress=False
                break
        if ProgressWindow.keepWindow==False: #If keep window is false, end progress window (useful to not have the progress window disappear and reappear between different progress situations of a same action chain)
            cmds.progressWindow( edit=True, endProgress=1)
    
    def update(status,count,maxCount=None,endStatus='',statusOnly=False): #Update progress window
        if ProgressWindow.show==False:
            return
        if maxCount!=None:
            ProgressWindow.progressMax=maxCount
            cmds.progressWindow( edit=True,
                maxValue=maxCount
            )
        if status==None:
            cmds.progressWindow( edit=True,
                progress=count
            )
        else:
            status=ProgressWindow.fixStatus(status,count)
            if statusOnly:
                cmds.progressWindow( edit=True,
                    status=f'{status}',
                    progress=count
                )
            else:
                cmds.progressWindow( edit=True,
                    status=f'{status} {count}/{ProgressWindow.progressMax}{endStatus}',
                    progress=count
                )
    
    def fixStatus(status,count): #Apply custom tags to status
        if status.count('<')>0 and status.count('>')>0:
            if count>1:
                status = status.replace('<plural>','s')
            else:
                status = status.replace('<plural>','')
        return status

    def stop(): #Force stop progress window
        ProgressWindow.inProgress=False
        ProgressWindow.keepWindow=False
        cmds.progressWindow( edit=True, endProgress=1)
        ProgressWindow.progressMax=-1
    
    def buildUI_Setting(): #Settings window
        toggle = 'Disable' if ProgressWindow.show else 'Enable'
        if ThemeColor.currentTheme=='dark': #Keep the default better looking for dark theme
                setting = cmds.confirmDialog(
                title='HOTKEY PARALLELS', message='Change pop-up progress window settings', messageAlign='center',
                button=['Force stop',toggle,'Cancel'],
                defaultButton='Cancel',
                parent=BuildWindow.windowName
            )
        else: #Use custom theme colors for the other themes
            setting = cmds.confirmDialog(
                title='HOTKEY PARALLELS', message=f'<font color={ThemeColor.txt_light}>Change progress window settings</font>', messageAlign='center',
                button=['Force stop',toggle,'Cancel'],
                defaultButton='Cancel',
                backgroundColor=ThemeColor.acColumn,
                parent=BuildWindow.windowName
            )
        if setting=='Force stop':
            ProgressWindow.stop()
        elif setting=='Enable':
            ProgressWindow.show=True
        elif setting=='Disable':
            ProgressWindow.show=False

class BuildWindow(object):
    #--- Variables ---
    window = None
    windowName = "HotkeyParallels_Window"
    windowTitle = "HOTKEY PARALLELS - 1.0.1 - [Maya 2024+]"
    windowSizable = True
    keepPos = True #Window will reset it's size but not it's position
    defaultTheme = 'dark'
    ThemeColor.setTheme(defaultTheme)
    
    mainLyt = None
    topLyt = None
    scrollAreaLayout = None
    elementsLayout = None
    actionsLayout = None
    refreshLayout = None
    refreshWaitRebuild = False
    refreshMltAsked = False
    refreshMltAllowed = False
    refreshMltCount = 0
    hideRemoved = False
    topBttn_UseInfo = "\n\n[Drag from the key's UI area with mouse middle button and drop over this button]\nor\n[Set file index on the input field then press this button]"
    intFieldCtrl = None
    intFieldMax = 2
    intFieldIdx = 0
    intFieldLockCtrl = None
    intFieldLock = False
    
    #--- UI ---
    #region - init
    def __init__(self):
        #Close old window if exists
        if cmds.window(self.windowName, exists=True):
            cmds.deleteUI(self.windowName, window=True)
        if cmds.windowPref(self.windowName, exists=True) and self.keepPos==False:
            cmds.windowPref(self.windowName, remove=True)
        
        #Create new window
        self.window = cmds.window(
            self.windowName,
            title=self.windowTitle,
            widthHeight=ThemeColor.winWH,
            sizeable=self.windowSizable,
            backgroundColor=ThemeColor.winBack
        )
        if self.keepPos==True:
            cmds.window(self.window, edit=True, sizeable=False)
        
        #UI
        main_formLyt = cmds.formLayout()
        
        main_mainAreaLyt = cmds.formLayout(
            margins=15,
            backgroundColor=ThemeColor.mainArea,
            parent=main_formLyt
        )
        BuildWindow.mainLyt = main_mainAreaLyt
        #region - Top area
        mainArea_topMainLyt = cmds.rowLayout(
            adjustableColumn=1,
            numberOfColumns=3,
            parent=main_mainAreaLyt
        )
        BuildWindow.topLyt = mainArea_topMainLyt
        mainArea_topLyt = cmds.flowLayout(
            height=30,
            columnSpacing=5,
            parent=mainArea_topMainLyt
        )
        cmds.separator(height=30,width=3,horizontal=False,style='none',parent=mainArea_topLyt)
        
        #Icons
        buildUI_TopIcon( #Import
            'fileOpen.png',
            30,30,mainArea_topLyt,
            'ParallelsCore.importFile()',
            'INFO: Import file(s)'
        )
        cmds.separator( height=30, width=6, style='none', parent=mainArea_topLyt )
        buildUI_TopIcon( #Clear all
            'UVTkDeleteInvalidSet.png',
            30,30,mainArea_topLyt,
            'ParallelsCore.reset_Files_HKData()',
            'INFO: Clear all files'
        )
        cmds.separator( height=30, width=2, style='none', parent=mainArea_topLyt )
        cmds.separator( height=30, width=2, style='none', backgroundColor=ThemeColor.topSeparator, parent=mainArea_topLyt )
        cmds.separator( height=30, width=2, style='none', parent=mainArea_topLyt )
        cmds.symbolCheckBox( #Toggle hide removed keys
            annotation='INFO: Hide removed keys (Toggle)',
            height=30, width=30,
            image='Bool_Hidden.png', highlightColor=ThemeColor.Bttn,
            onCommand='ParallelsCore.setHideRemoved(True)', offCommand='ParallelsCore.setHideRemoved(False)',
            parent=mainArea_topLyt
        )
        cmds.separator( height=30, width=2, style='none', parent=mainArea_topLyt )
        cmds.separator( height=30, width=2, style='none', backgroundColor=ThemeColor.topSeparator, parent=mainArea_topLyt )
        cmds.separator( height=30, width=2, style='none', parent=mainArea_topLyt )
        buildUI_TopIcon( #Remove
            'deletePCM.png',
            30,30,mainArea_topLyt,
            'bttn_TopPress(0)',
            f'INFO: Remove file {BuildWindow.topBttn_UseInfo}    ',
            "dropCallback_Remove('%(dragControl)s')"
        )
        cmds.separator( height=30, width=6, style='none', parent=mainArea_topLyt )
        buildUI_TopIcon( #Set as main file
            'editPCM.png',
            30,30,mainArea_topLyt,
            'bttn_TopPress(1)',
            f'INFO: Set as reference Hotkey file {BuildWindow.topBttn_UseInfo}    ',
            "dropCallback_SetMainFile('%(dragControl)s')"
        )
        buildUI_TopIcon( #Move file to the left
            'UVTkArrowLeft.png',
            30,30,mainArea_topLyt,
            'bttn_TopPress(2)',
            f'INFO: Move file column to the left {BuildWindow.topBttn_UseInfo}    ',
            "dropCallback_Reorder(True, '%(dragControl)s')"
        )
        buildUI_TopIcon( #Move file to the right
            'UVTkArrowRight.png',
            30,30,mainArea_topLyt,
            'bttn_TopPress(3)',
            f'INFO: Move file column to the right {BuildWindow.topBttn_UseInfo}    ',
            "dropCallback_Reorder(False, '%(dragControl)s')"
        )
        cmds.separator( height=30, width=6, style='none', parent=mainArea_topLyt )
        BuildWindow.intFieldCtrl = cmds.intField( #Index input field
            annotation='INFO: Set file index (left to right and starting by 1) to be used when clicking on the near buttons.\nSet at 0 to disable\n\n[Enter] to confirm or [Ctrl+Mouse left] to slide values',
            height=30, width=40,
            minValue=0, maxValue=2, step=1,
            changeCommand="bttn_setIntFieldIDX()",
            enterCommand="bttn_setIntFieldIDX()",
            enableKeyboardFocus=False,
            backgroundColor=ThemeColor.idxFieldBack,
            parent=mainArea_topLyt
        )
        intFieldArrowLyt=None
        if ThemeColor.topIDXArrwBack==None:
            intFieldArrowLyt = cmds.flowLayout(
                height=30, width=15,
                horizontal=False,
                parent=mainArea_topLyt
            )
        else:
            intFieldArrowLyt = cmds.flowLayout(
                height=30, width=15,
                horizontal=False,
                backgroundColor=ThemeColor.topIDXArrwBack,
                parent=mainArea_topLyt
            )
        buildUI_TopIcon( #Increase intField's value
            'arrowUp.png',
            15,15,intFieldArrowLyt,
            'bttn_setIntFieldValue(True)',
            'INFO: Increase the file index'
        )
        buildUI_TopIcon( #Decrease intField's value
            'arrowDown.png',
            15,15,intFieldArrowLyt,
            'bttn_setIntFieldValue(False)',
            'INFO: Decrease the file index'
        )
        BuildWindow.intFieldLockCtrl = cmds.symbolCheckBox( #Lock intField to edited order
            annotation="INFO: Update file index field to match the new index when the file at this index changes of order (Toggle)",
            height=20, width=20,
            image='lockGeneric.png', highlightColor=ThemeColor.Bttn,
            onCommand='setIntFieldLock(True)', offCommand='setIntFieldLock(False)',
            parent=mainArea_topLyt
        )
        buildUI_TopIcon( #Stop progress
            'alignSurface.svg',
            30,30,mainArea_topMainLyt,
            'ProgressWindow.buildUI_Setting()',
            'INFO: Settings for the pop-up progress window'
        )
        buildUI_TopIcon( #Theme
            'advancedSettings.png',
            30,30,mainArea_topMainLyt,
            'buildUI_SetTheme()',
            'INFO: Settings for the window theme'
        )
        #endregion - Main area | Top

        buildUI_ScrollArea() #Scroll area

        #region - Help line area
        main_helpLyt = cmds.rowLayout(
            backgroundColor=ThemeColor.hLBack,
            margins=5,
            adjustableColumn=1,
            parent=main_formLyt
        )
        cmds.helpLine(
            height=25,
            statusBarMessage='INFO: Help line, explains you what your cursor is over',
            parent=main_helpLyt
        )
        #endregion - Help line area

        #region - Setup end
        #--- Setup main_formLyt now the main elements are generated ---
        cmds.formLayout(
            main_formLyt, edit=True,
            attachForm=((main_mainAreaLyt, 'top', 0), (main_mainAreaLyt, 'left', 0), (main_mainAreaLyt, 'right', 0),
                        (main_helpLyt, 'left', 0), (main_helpLyt, 'right', 0), (main_helpLyt, 'bottom', 0)),
            attachControl=((main_mainAreaLyt, 'bottom', 0, main_helpLyt))
        )

        #Display window
        cmds.showWindow()
        if self.keepPos:
            cmds.window(self.window, edit=True, sizeable=self.windowSizable)
        #endregion - Setup end
    #endregion - init
    
    #--- Functions ---

class ParallelsCore():
    #--- Variables ---
    #Dictionnary for the HKDatas of the files
    files_HKData = {}
    files_idx = []
    files_actions = []
    files_rtmCmds = []
    files_actionsCount = {}
    aCTotalName = 'HKP_Total'
    files_actionsMainFile = []
    files_columnsCount = 5 #Not the exact count of files! Extra two when over five
    files_removedCount = 0
    files_filesCount = 0

    #--- Functions ---
    def clean_HotkeysChunk(data=''): #Clean an extracted hotkeysChunk because Maya sometimes mixes hotkey lines and other lines
        ctx_count = data.count(';\nhotkeyCtx')
        i=0
        while i < ctx_count:
            idx_start = data.find(';\nhotkeyCtx')+2 #Find the beginning of the first current hotkeyCtx line
            idx_end = data[idx_start:].find(';')+2 +idx_start #Find the end of the first current hotkeyCtx line
            data = data[:idx_start] + data[idx_end:] #Recreate data with before and after the first current hotkeyCtx line
            i+=1
        return data
    
    def build_HotkeyData(commandName='', shortcut='', ctrl=False, shift=False, alt=False, onPress=False, onRelease=False, repeatable=False, customScript=False, removed=False): #Build stuctured data for one hotkey
        #Modifiers
        modifiers = [ ctrl, shift, alt ]
        #Extra
        extra = [ onPress, onRelease, repeatable, customScript ]
        #HotkeyData
        hotkeyData = [ commandName, shortcut, modifiers, extra, removed ]
        return hotkeyData

    def importFile(): #Import hotkey file(s) content, extract infos and store them
        if BuildWindow.refreshLayout!=None:
            clearUI_RefreshUIConfirm()

        fileFilter = '*.mhk'
        newPaths = cmds.fileDialog2(
            caption='Pick Maya hotkey file(s) (.mhk)',
            fileFilter=fileFilter, fileMode=4, # 1->output one file ; 2->output directory and file(s) ; 4->output one or many file(s)
            hideNameEdit=False, setProjectBtnEnabled=False
        )
        if newPaths==None:
            return
        
        pathIndex=0
        removedCount = 0
        pathCount = len(newPaths)
        ProgressWindow.buildUI('Importing file<plural>', pathCount, True)
        for path in newPaths:
            if pathIndex>0:
                ProgressWindow.update('Importing file<plural>', pathIndex)
            
            #Get file name and reference it in the files HK Data
            fileName = path.rsplit('/', 1)[1]
            ParallelsCore.files_HKData[fileName] = {}
            if ParallelsCore.files_idx.count(fileName) == 0: #Check if the file isn't already on the index list, if so don't add it again
                ParallelsCore.files_idx.append(fileName)
                ParallelsCore.files_filesCount += 1
            #Open file until 'with' ends which automatically call .close()
            with open(path, 'r', encoding='utf-8') as f:
                f_data = f.read()
                #Find different words in the file to get indexes of the start and end of the wanted parts and save them in an array
                # *runTimeCommands*
                idx_start = f_data.find('runTimeCommand')
                temp_fData = f_data[ idx_start : f_data.count('')-1 ]
                idx_end = temp_fData.find('\n//')+idx_start

                runTimeCommands_idxs = [ idx_start, idx_end ]
                runTimeCommands_chunk = f_data[ runTimeCommands_idxs[0]: runTimeCommands_idxs[1] ]
                # *nameCommands*
                idx_start = f_data.find('nameCommand')
                idx_end = f_data.rfind('NameCommand;')+12

                nameCommands_idxs = [ idx_start, idx_end ]
                nameCommands_chunk = f_data[ nameCommands_idxs[0]: nameCommands_idxs[1] ]
                # *hotkeys*
                idx_start = f_data.find('hotkey -keyShortcut')
                idx_lastHK = f_data.rfind('hotkey -keyShortcut')
                idx_end = f_data.find(';', idx_lastHK)+1
                
                hotkeys_chunk = f_data[idx_start: idx_end]
                hotkeys_chunk = ParallelsCore.clean_HotkeysChunk(hotkeys_chunk) #Clean the hotkeys_chunk of hotkeyCtx lines that Maya can mix up with hotkey lines

                #Generate dictionnary for the HKDatas of this file
                f_HKData = {}
                hk_data = [] #List that will be replaced for each hotkey
                hk_dataName = ''

                #Find how much hotkeys should be in the file
                hk_count = hotkeys_chunk.count('-keyShortcut')
                idx_start = 0
                idx_end = 0
                #Find characters length of the chunk and minus one since the range starts at 0
                hk_fixedlength = hotkeys_chunk.count('')-1
                i=0
                for i in range(hk_count):
                    #Info to extract
                    hk_command=''
                    hk_commandName=''
                    hk_hotkey=''
                    hk_ctrl=False
                    hk_shift=False
                    hk_alt=False
                    hk_onPress=False
                    hk_onRelease=False
                    hk_repeatable=False
                    hk_customScript=False
                    hk_removed=False

                    #Hotkey - Get hotkey between the two first '"' in the hotkeys_chunk and starting at previous start index idx_start
                    temp_s = idx_start
                    idx_start = hotkeys_chunk[temp_s: hk_fixedlength].find('"') +1 +temp_s
                    idx_end = hotkeys_chunk[idx_start: hk_fixedlength].find('"') + idx_start
                    hk_hotkey = hotkeys_chunk[idx_start: idx_end]

                    #CommandName - Get commandName between '("' and '")' in the hotkeys_chunk and starting at previous start index idx_start
                    idx_start = hotkeys_chunk[temp_s: hk_fixedlength].find('("') +2 +temp_s
                    idx_end = hotkeys_chunk[idx_start: hk_fixedlength].find('")') + idx_start
                    hk_commandName = hotkeys_chunk[idx_start: idx_end]
                    if hk_commandName == '': #If commandName empty, this hotkeyline is about a removed hotkey
                        hk_removed=True
                        removedCount+=1
                    else: #Else remove the nameCommand suffix not matching the runtime command display in Maya's hotkey editor
                        hk_commandName = hk_commandName[:-11]

                    #Set idx_start to the end of this hotkey line
                    idx_start = hotkeys_chunk[temp_s: hk_fixedlength].find(';') +2 +temp_s
                    
                    #Modifiers - Find if modifiers and extra are referenced in the current hotkey line between it's start and before the nameCommand
                    temp_Line = hotkeys_chunk[temp_s: idx_start]
                    if temp_Line.find('-ctl') != -1:
                        hk_ctrl=True
                    if temp_Line.find('-sht') != -1:
                        hk_shift=True
                    if temp_Line.find('-alt') != -1:
                        hk_alt=True
                    # Extra
                    if temp_Line.find('-name') != -1:
                        hk_onPress=True
                    if temp_Line.find('-releaseName') != -1:
                        hk_onRelease=True
                    if temp_Line.find('-pressCommandRepeat true') != -1:
                        hk_repeatable=True
                    
                    if hk_removed != True: #If removed, no commandName so nameCommand can't be found and then customScript can't be found either among runTimeCommands
                        #Command - Get command from nameCommands_chunk
                        nc_fixedCount = nameCommands_chunk.count('')-1
                        temp_s = nameCommands_chunk.find(hk_commandName)
                        temp_idx_start = nameCommands_chunk[temp_s: nc_fixedCount].find('("') +2 +temp_s
                        temp_idx_end = nameCommands_chunk[temp_idx_start: nc_fixedCount].find('")') +temp_idx_start
                        hk_command = nameCommands_chunk[temp_idx_start: temp_idx_end]
                        
                        #CustomScript - Find if command is among the runTimeCommands_chunk
                        if runTimeCommands_chunk != '':
                            if runTimeCommands_chunk.find(f'{hk_command};') != -1:
                                hk_customScript=True
                    
                    #Build hk_data and add/update it to the file_HKData
                    hk_data = ParallelsCore.build_HotkeyData(
                        hk_commandName, hk_hotkey,
                        hk_ctrl, hk_shift, hk_alt,
                        hk_onPress, hk_onRelease, hk_repeatable, hk_customScript, hk_removed
                    )
                    if hk_removed: #Name according to the eventual data
                        hkName = f"{'[REL]' if hk_onRelease else ''}{'[PRSS]' if hk_onRelease else ''}{'[REP]' if hk_repeatable else ''}{'Ctrl+' if hk_ctrl else ''}{'Shift+' if hk_shift else ''}{'Alt+' if hk_alt else ''}{hk_hotkey}"
                        hk_dataName = f'HKP_Removed_({hkName})_HKData'
                    else:
                        hk_dataName = f'{hk_command}_HKData'
                    if hk_dataName in f_HKData: #If there is already a key with this name in the file's data, iterate it
                        hk_dataName = ParallelsCore.iterate_HKName(hk_dataName, list(f_HKData.keys()))
                    f_HKData[hk_dataName] = hk_data
                
                #Add/Update f_HKData to the files_HKData
                ParallelsCore.files_HKData[fileName] = f_HKData
            pathIndex+=1
        newIdxCount = ParallelsCore.files_filesCount
        if newIdxCount > 2: #If current index count higher than two, set it as int field and stored max value
            cmds.intField( BuildWindow.intFieldCtrl, edit=True, maxValue=newIdxCount )
            BuildWindow.intFieldMax = newIdxCount

        ParallelsCore.build_Actions()
    
    def iterate_HKName(hk_name:str, hk_keys:list): #Add iteration on the name and if already exists in the list, increase it and retry
        found = False
        name = hk_name.rsplit('_',1)
        fName = ''
        idx = 1
        while found==False:
            fName = f"{name[0]}_{'{:02}'.format(idx)}_{name[1]}"
            if hk_keys.count(fName) == 0:
                found=True
            else:
                idx+=1
        return fName

    def build_Actions(): #Build actions data and then actions UI column and file(s) UI column(s)
        values = ParallelsCore.files_HKData.values()
        filesKey = list(ParallelsCore.files_HKData.keys())
        ParallelsCore.files_actionsCount.clear()
        aCTotal = ParallelsCore.aCTotalName
        ParallelsCore.files_actionsMainFile.clear()

        #Get the content of each file in files_HKData, then each key inside it and if isn't already in files_actions, add it
        isMainFile=False
        index=0
        cFileKey = None
        valuesCount=len(values)
        ProgressWindow.update(f'Building data for file',1,valuesCount,'',True)
        for item in values:
            cFileKey = filesKey[index]
            isMainFile = True if ParallelsCore.files_idx[0] == cFileKey else False
            keys=item.keys()
            cKeyIndex=0
            cKeyCount=len(keys)
            for key in keys:
                ProgressWindow.update('Building data',cKeyIndex,None,f' for file {index+1}/{valuesCount}')
                keyFixed = key.replace('_HKData', '')
                if ParallelsCore.files_actions.count(keyFixed) == 0: #Add action to files_actions only if it isn't already in it
                    ParallelsCore.files_actions.append(keyFixed)
                    #RemovedCount
                    if key.count('HKP_Removed_') == 1:
                        ParallelsCore.files_removedCount += 1
                if isMainFile: #Register action as among main file actions
                    ParallelsCore.files_actionsMainFile.append(keyFixed)

                #ActionsCount
                if keyFixed not in ParallelsCore.files_actionsCount: #If the action doesn't exist in actionsCount, add it with default 0 for every files
                    tempDic = {}
                    tempDic[aCTotal] = 0 #Add a total value for the action which will be quicker to check than calculating it
                    for fileIDX in ParallelsCore.files_idx:
                        tempDic[fileIDX] = 0
                    ParallelsCore.files_actionsCount[keyFixed] = tempDic
                #Increase action's total value and value for the current file key
                ParallelsCore.files_actionsCount[keyFixed][aCTotal] += 1
                ParallelsCore.files_actionsCount[keyFixed][cFileKey] += 1
                cKeyIndex+=1
            index+=1
        ProgressWindow.update('Building data extras',0,1)
        #Sort the actions list according to a 'lambda' function that will return (bool, str) from the given key
        # bool according to if the key contains 'HKP_Removed_'
        # str according to the key written in lower case so cases don't impact the order
        ParallelsCore.files_actions.sort( key=lambda x:('HKP_Removed_' in x, str.casefold(x)) )
        #ParallelsCore.files_actionsMainFile.sort( key=lambda x:('HKP_Removed_' in x, str.casefold(x)) ) #                          ////// For ease of debug but unecessary //////
        ParallelsCore.build_RtmCmds()
        #Build scroll area UI to prepare for the actions' and files' UIs
        ProgressWindow.update(f'Building UI',1,None,'',True)
        columnsAmount = ParallelsCore.files_filesCount+1 #+1 for the action column
        if columnsAmount > 5: #Make sure the rowLayout's numberOfColumns follows the number if more than 5 (arbitrary value)
            ParallelsCore.files_columnsCount = columnsAmount+2 #Keep a safe margin of two
            buildUI_ScrollArea() #Require reset scrollArea, rowLayout's numberOfColumns doesn't support edit
        else:
            ParallelsCore.files_columnsCount = 5
            clearUI()
        
        buildUI_ActionsFiles(True)
        ProgressWindow.stop()

    def build_RtmCmds(): #Build the files_rtmCmds list
        ParallelsCore.files_rtmCmds.clear()
        #Store ParallelsCore variables for quicker access
        HKData = ParallelsCore.files_HKData
        acCountList = ParallelsCore.files_actionsCount
        fileIDXList = ParallelsCore.files_idx
        actionSuffix = '_HKData'
        rtmCmds = []
        for action in ParallelsCore.files_actions: #For each action check for each file in the index order if they have in the files_actionsCount this action
            for fileName in fileIDXList:
                if acCountList[action][fileName] == 1: #If so, get the runtim command from the file's HKData, add it to the rtmCmds list and skip to next action
                    acCmd = HKData[fileName][f'{action}{actionSuffix}'][0]
                    if acCmd=='':
                        acCmd=None
                    rtmCmds.append(acCmd)
                    break
        ParallelsCore.files_rtmCmds = rtmCmds

    def removeFile(fileName): #Remove file fileName
        needRebuild=False
        if ParallelsCore.files_idx.count(fileName) == 0:
            cmds.error(f"Couldn't find file ' {fileName} ' in the data built from imported files", n=True)
        else:
            mainFile = True if ParallelsCore.files_idx[0]==fileName else False #Get if this is the main file
            ParallelsCore.files_HKData.pop(fileName) #Remove from data dictionnary and index list
            ParallelsCore.files_idx.remove(fileName)
            ParallelsCore.files_filesCount-=1
            
            #Update files_actionsCount
            aCTotal = ParallelsCore.aCTotalName
            actionsToRemove = []
            rtmCmds = ParallelsCore.files_rtmCmds
            removedCounter = 0
            index=0
            for action in ParallelsCore.files_actions:
                cTotal = ParallelsCore.files_actionsCount[action][aCTotal]
                if ParallelsCore.files_actionsCount[action][fileName] == 1 and cTotal > 0: #Reduce the count total of the action if it was used by the file to remove and is not already at zero
                    ParallelsCore.files_actionsCount[action][aCTotal] -= 1
                    cTotal -= 1
                if cTotal <= 0: #Action no more used by any file, remove it
                    actionsToRemove.append(action) #Store the actions to be removed after, if removed directly would mess the for loop
                    rtmCmds.pop(index-removedCounter) #Remove the runtime command according the the index less already removed item(s) that have then dynamically dicreased the list's index equivalent
                    removedCounter+=1
                else: #Remove only the count of this file for this action
                    del ParallelsCore.files_actionsCount[action][fileName]
                index+=1
            
            for action in actionsToRemove: #Actually remove actions from the actions list
                ParallelsCore.files_actions.remove(action)
                del ParallelsCore.files_actionsCount[action]
                if action.count('HKP_Removed_')==1: #If Removed action, reduce the Removed count
                    ParallelsCore.files_removedCount -= 1
                    if needRebuild==False:
                        needRebuild=True

            #If mainFile, update files_actionsMainFile
            if mainFile:
                ParallelsCore.files_actionsMainFile.clear()
                #Update files_actionsMainFile
                HKDataValues = ParallelsCore.files_HKData.values()
                for item in HKDataValues:
                    for key in item.keys():
                        keyFixed = key.replace('_HKData', '')
                        ParallelsCore.files_actionsMainFile.append(keyFixed)
                    break
            
            newIntFMax = BuildWindow.intFieldMax-1 #Update int field UI's max value and stored value in BuildWindow if needed
            listLen = ParallelsCore.files_filesCount
            if newIntFMax >= 2:
                if BuildWindow.intFieldIdx > newIntFMax: #If current int field in on the higher than the new max, update it and the stored value to the new max
                    cmds.intField( BuildWindow.intFieldCtrl, edit=True, value=newIntFMax )
                    BuildWindow.intFieldIdx = newIntFMax
                cmds.intField( BuildWindow.intFieldCtrl, edit=True, maxValue=newIntFMax ) #Update the int field and stored max value
                BuildWindow.intFieldMax = newIntFMax
            else: #No max update since it has to stay at 2
                if newIntFMax == listLen or listLen==0: #Only update the index if it is higher than the files_idx's length (//+1-1 so equal newIntMax) or there is no more file
                    cmds.intField( BuildWindow.intFieldCtrl, edit=True, value=listLen )
                    BuildWindow.intFieldIdx = listLen
            
        return needRebuild
    
    def setAsMainFile(fileName,doIntLock=True): #Set new main file from the fileName
        if ParallelsCore.files_idx[0] == fileName:
            return
        ParallelsCore.files_idx.sort( key=lambda x:0 if x==fileName else 1 ) #Reorder the files_idx list to have fileName first
        ParallelsCore.files_actionsMainFile.clear()
        for action in ParallelsCore.files_HKData[fileName].keys():
            actionFixed = action.replace('_HKData', '')
            ParallelsCore.files_actionsMainFile.append(actionFixed)
        if BuildWindow.intFieldLock and doIntLock: #If asked, update intField value to match
            updateIntField(1)
        buildUI_RefreshUIConfirm()

    def setHideRemoved(hide:bool): #Set the hide removed value and update UI accordingly
        BuildWindow.hideRemoved=hide
        if ParallelsCore.files_filesCount == 0 or ParallelsCore.files_removedCount == 0 or BuildWindow.refreshLayout != None: #If no UI, no Removed actions UI or already displaying refresh confirmation layout, don't continue
            return
        if hide and ParallelsCore.files_removedCount>0: #If going to hide and already has HKP_Removed_ actions on the UI, ask rebuild scroll area and refresh UI
            BuildWindow.refreshWaitRebuild = True
            buildUI_RefreshUIConfirm()
        else: #Else no need to rebuild scroll area, updateUI_ScrollArea() should be enough
            buildUI_RefreshUIConfirm()

    def reset_Files_HKData(scrollArea=True): #Reset every stored data and rebuild the scroll area UI to prevent it from keeping changes from old UIs (like height or width of the scrollable area)
        ParallelsCore.files_HKData.clear()
        ParallelsCore.files_idx.clear()
        ParallelsCore.files_filesCount = 0
        ParallelsCore.files_actions.clear()
        ParallelsCore.files_rtmCmds.clear()
        ParallelsCore.files_actionsCount.clear()
        ParallelsCore.files_actionsMainFile.clear()
        ParallelsCore.files_columnsCount = 5
        ParallelsCore.files_removedCount = 0
        BuildWindow.intFieldIdx = 0
        BuildWindow.intFieldMax = 2
        cmds.intField( BuildWindow.intFieldCtrl, edit=True, value=0, maxValue=2 )
        clearUI_RefreshUIConfirm()
        if scrollArea:
            buildUI_ScrollArea(True)

scriptWindow = BuildWindow()