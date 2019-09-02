import PySimpleGUI as sg
from PIL import Image

# All the stuff inside your window. This is the PSG magic code compactor...
from EbayProductFinding import getProductsForRecommender
from RecommenderSystem import recommendUser


layout = [
            [sg.Text('Twitter Handle:')],
            [sg.InputText(size=(100,6))],
            [sg.Listbox(values=['','', '','',''], size=(100, 6),key="items")],
            [sg.Image(r'',size=(100, 100),key="item0"),sg.T(' '  * 10), sg.Image(r'',size=(100, 100), key="item1")
             ,sg.T(' '  * 10),sg.Image(r'',size=(100, 100), key="item2"),sg.T(' '  * 10), sg.Image(r'',size=(100, 100), key="item3")
             ,sg.T(' '  * 10),sg.Image(r'',size=(100, 100), key="item4")],
            [sg.OK(), sg.Cancel()]]

# Create the Window
window = sg.Window('Dena', layout)
# Event Loop to process "events"
while True:
    event, values = window.Read()

    if event == 'OK':
        recItems = recommendUser(values[0])
        window.FindElement('item0').Update("Item0.png")
        window.FindElement('item1').Update("Item1.png")
        window.FindElement('item2').Update("Item2.png")
        window.FindElement('item3').Update("Item3.png")
        window.FindElement('item4').Update("Item4.png")
        window.FindElement('items').Update(recItems)
    if event in (None, 'Cancel'):
        break

window.Close()