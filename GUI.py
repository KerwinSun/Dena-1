import PySimpleGUI as sg

import EbayProductFinding
from PIL import Image
# All the stuff inside your window. This is the PSG magic code compactor...
from RecommenderSystem import recommendUser
from SemanticNetRecomender2WikiepdiaAPI import doUserAnalysis

tab1_layout = [
            [sg.Text('Twitter Handle:')],
            [sg.InputText(size=(100,6))],
            [sg.Listbox(values=['','', '','',''], size=(100, 6),key="items")],
            [sg.Image(r'',size=(100, 100),key="item0"),sg.T(' '  * 10), sg.Image(r'',size=(100, 100), key="item1")
             ,sg.T(' '  * 10),sg.Image(r'',size=(100, 100), key="item2"),sg.T(' '  * 10), sg.Image(r'',size=(100, 100), key="item3")
             ,sg.T(' '  * 10),sg.Image(r'',size=(100, 100), key="item4")],
            [sg.Button('recommender'), sg.Cancel()]]

tab2_layout = [
            [sg.Text('Twitter Handle:')],
            [sg.InputText(size=(100,6))],
            [sg.Listbox(values=[''], size=(100, 6), enable_events=True, key="items2")],
            [sg.Image(r'',size=(200, 200),key="B_Image")],
            [sg.Button('naive'), sg.Cancel()]]

layout = [[sg.TabGroup([[sg.Tab('Tab 1', tab1_layout), sg.Tab('Tab 2', tab2_layout)]])]]

# Create the Window
window = sg.Window('Dena', layout)
# Event Loop to process "events"
while True:
    event, values = window.Read()

    if event == 'recomender':
        recItems = recommendUser(values[0])
        window.FindElement('item0').Update("Item0.png")
        window.FindElement('item1').Update("Item1.png")
        window.FindElement('item2').Update("Item2.png")
        window.FindElement('item3').Update("Item3.png")
        window.FindElement('item4').Update("Item4.png")
        window.FindElement('items').Update(recItems)

    if event == 'naive':
        recItems = doUserAnalysis(values[1])
        window.FindElement('items2').Update(recItems)
    if event == 'items2':
        entityCount = values['items2'][0][1]
        print(entityCount)
        window.FindElement("B_Image").Update("assets/B_Item" + entityCount + ".png")
    if event in (None, 'Cancel'):
        break

window.Close()