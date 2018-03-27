#! /usr/bin/env python
# -*- coding: UTF8 -*-
# Este arquivo é parte do programa Kwarwp
# Copyright 2010-2018 Carlo Oliveira <carlo@nce.ufrj.br>,
# `Labase <http://labase.selfip.org/>`__; `GPL <http://j.mp/GNU_GPL3>`__.
#
# Kwarwp é um software livre; você pode redistribuí-lo e/ou
# modificá-lo dentro dos termos da Licença Pública Geral GNU como
# publicada pela Fundação do Software Livre (FSF); na versão 2 da
# Licença.
#
# Este programa é distribuído na esperança de que possa ser útil,
# mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO
# a qualquer MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, veja em <http://www.gnu.org/licenses/>

"""Brython front end client.

.. moduleauthor:: Carlo Oliveira <carlo@nce.ufrj.br>

"""
import sys

CANVASW, CANVASH = 800, 600

CENAS = ["{}".format(chr(a)) for a in range(ord('a'), ord('z') + 1) if chr(a) not in 'aeiouy']
EDTST = {'position': 'relative', 'padding': 10, 'margin': '0', 'flex': '3 1 auto',
         'width': '99%', 'resize': 'none', 'borderColor': 'darkslategrey',
         'color': 'navajowhite', 'border': 1, 'background': 'rgba(10, 10, 10, 0.5)'}
ERRST = {'position': 'relative', 'padding': 10, 'margin': '0', 'visibility': 'visible', 'flex': '1',
         'width': '99%', 'min-height': '30%', 'resize': 'none', 'borderColor': 'darkslategrey',
         'color': 'navajowhite', 'border': 1, 'background': 'rgba(200, 54, 54, 0.5)'}


class Dialog:
    def __init__(self, gui, text='xxxx', act=lambda x: None):

        divat = {'position': 'absolute', 'top': 64, 'left': 0, 'display': 'flex', 'padding': '7px',
                 'flex-direction': 'column', 'align-items': 'stretch',
                 'width': '786px', 'height': '536px', 'background': 'rgba(10, 10, 10, 0.85)'}
        self.text = text
        self.gui = gui
        self.html, self.dom = gui.html, gui.dom
        self._div = self._err = self._area = None
        self._div = self._div if self._div else self.html.DIV(style=divat)
        self.dom <= self._div
        text = text if text else self.text
        self._area = self.textarea(text, style=EDTST)
        self._set_code()
        self.edit = gui.edit
        gui.edit = self.action
        self.act = act

    def _set_code(self):
        self._div <= self._area
        self.__area = self.gui.window.CodeMirror.fromTextArea(
            self._area, dict(mode="python", theme="solarized", lineNumbers=True))
        self._doc = self.__area.getDoc()

    def textarea(self, text, style=EDTST):
        t = self.html.TEXTAREA(text, style=style)
        return t

    def remove(self):
        self._div.remove()
        # self._area.remove()

    def hide(self):
        self.remove()
        # self._rect.style.visibility = 'hidden'
        # self._area.style.visibility = 'hidden'

    def show(self):
        # self._rect.style.visibility = 'visible'
        # self._set_code()
        # self._area.style.visibility = 'visible'
        self._div.style.visibility = 'visible'

    def _update_text(self):
        self.text = self._area.value
        return self.text

    def get_text(self):
        self.__area.save()
        self.text = ''
        return self.text if self.text else self._update_text()

    def set_err(self, text):
        self._err.remove() if self._err else None
        self._err = self.textarea(text, style=ERRST)
        self._div <= self._err
        self.text = ''
        error = text
        lines = error.split(' line ')
        if len(lines) > 1:
            try:
                line = int(lines[-1].split("\n")[0])
                _ = error.split("\n")[-2]
                _ = self._doc.setSelection(dict(line=line-1, ch=0), dict(line=line-1, ch=60))
            except Exception as x:
                print("Exception", x)

    def del_err(self):
        self._err.remove() if self._err else None
        self._err = None

    def set_text(self, text):
        self._area.value = text

    def action(self, *_):
        self.text = self._area.value
        self.hide()
        self.gui.edit = self.edit
        self.act(self)


class Game:
    def __init__(self, gui, traceback, width=CANVASW, height=CANVASH, code=None,  codename=None, **kwargs):
        self.html, doc, self.code, self.window = gui.html, gui.doc, code, gui.win
        self.storage,  self.codename = gui.sto,  codename
        self.executante, self.traceback = None, traceback
        self.dialogue = self.code = None
        self.dom = doc["pydiv"]
        self.document = doc
        self.events = {}
        self.edit = self._edit

    def run(self):
        self.executante()

    def _edit(self, *_):
        self.dialog("", act=self.executa_acao)

    def dialog(self, text=None, act=lambda x: None):
        text = text if text else self.code
        if self.dialogue:
            self.dialogue.remove()
        self.dialogue = Dialog(self, text=text, act=act)
        self.dialogue.set_text(text)
        self.dialogue.show()
        return self.dialogue

    def _first_response(self, dialog, action):
        class ConsoleOutput:

            def __init__(self):
                self.value = ''

            def write(self, data):
                self.value += str(data)

            def flush(self):
                self.value = ''
                pass

        value = self.value = ConsoleOutput()
        sys_out, sys.stdout = sys.stdout, value
        sys_err, sys.stderr = sys.stderr, value
        # logger('first response %s %s %s' % (dialog, sys.stdout, sys.stderr))
        # TODO action += self.challenge[1]
        # logger('first response code %s' % action)
        try:
            action()
        except Exception as err:
            # except Exception as err:
            self.traceback.print_exc(file=sys.stderr)
            sys.stdout = sys_out
            sys.stderr = sys_err
            dialog = self.dialog(self.code, act=self.executa_acao)  # +str(self.value.value))
            dialog.set_err(str(self.value.value))
        else:
            self.code = dialog.get_text()
            pass
        sys.stdout = sys_out
        sys.stderr = sys_err

    def _executa_acao(self):
        exec(self.code, globals())

    def executa_acao(self, dialog):
        self.code = dialog.get_text()
        self.storage[self.codename] = self.code
        self._first_response(dialog, self._executa_acao)

    def registra_executante(self, executante):
        self.executante = executante
        self._first_response(self.dialogue, executante)


class Main:
    def __init__(self, br):
        self.doc, self.ht, self.alert, self.storage = br.document, br.html, br.alert, br.storage

    def _paint_scenes(self):
        """

        :return: 
        """
        ht = self.ht
        pyd = self.doc["pydiv"]
        pyd.html = ''
        sky = ht.DIV(style={'position': 'absolute', 'top': 0, 'left': 0})
        sky <= ht.IMG(src="image/sky.gif")
        sun = ht.DIV(
            id='the_sun', style={'position': 'absolute', 'top': 0, 'left': 0,
                                 'animation-name': 'daylight', 'animation-duration': '300s'})
        sun <= ht.IMG(src="image/sun.gif")
        pyd <= sky
        svg = ht.SVG(id="svgdiv", width="800", height="66")
        svg.setAttribute('height', "66")
        pyd <= svg
        pyd <= ht.DIV(id='selector', style={
            'position': 'relative', 'margin-top': '4px', 'display': 'flex',
            'max-width': '800px', 'flex-wrap': 'wrap', 'padding': '10px'})
        pyd <= sun

    def select_scene(self, scene):
        self.alert('foi' + scene)

    def paint_scenes(self):
        ht = self.ht
        self._paint_scenes()
        for count, scene in enumerate(CENAS):
            icon = ht.DIV()  # , onclick=lambda *_: self.select_scene(scene))
            icon.setAttribute("style", 'flex:1;min-width: 160px; flex-wrap: wrap; margin: 10px;' +
                              'background-color: navajowhite; border-radius: 60px; padding:4px;')
            style = {'width': '60px', 'height': '60px', 'padding': '20px', 'overflow': 'hidden',
                     'background': 'url(image/garden.jpg) no-repeat 0 0',
                     'background-position-x': '{}px'.format(-100 * (count % 5)),
                     'background-position-y': '{}px'.format(-100 * (count // 5))}

            # icon.onclick = lambda ev: self.select_scene(ev.target.id)
            # img.onclick = lambda ev: self.select_scene(ev.target.title)
            div, span, legend = ht.DIV(Id='proj_'+scene, style=style), ht.H6(scene, style={'text-align': 'center'}),\
                ht.LEGEND(scene)
            div.onclick = lambda ev: self.select_scene(ev.target.id)
            # div <= img
            icon <= span
            icon <= div
            self.doc['selector'] <= icon


def main(**kwargs):
    Main(**kwargs)


if __name__ == '__main__':
    main(**{})

PZ = ['afghanistan', 'albania', 'algeria', 'andorra', 'angola', 'antigua', 'argentina', 'armenia', 'australia',
      'austria', 'azerbaijan', 'bahamas', 'bahrain', 'bangladesh', 'barbados', 'belarus', 'belgium', 'belize', 'benin',
      'bhutan', 'bolivia', 'bosnia', 'botswana', 'brazil', 'brunei', 'bulgaria', 'burkina', 'burundi', 'cabo_verde',
      'cambodia', 'cameroon', 'canada', 'african_rep', 'chad', 'chile', 'china', 'colombia', 'comoros', 'dr_congo',
      'r_congo', 'costa_rica', 'ivoire', 'croatia', 'cuba', 'cyprus', 'czech_rep', 'denmark', 'djibouti', 'dominica',
      'dominican_rep', 'ecuador', 'egypt', 'el_salvador', 'eq_guinea', 'eritrea', 'estonia', 'ethiopia', 'fiji',
      'finland', 'france', 'gabon', 'gambia', 'georgia', 'germany', 'ghana', 'greece', 'grenada', 'guatemala', 'guinea',
      'guinea-bissau', 'guyana', 'haiti', 'honduras', 'hungary', 'iceland', 'india', 'indonesia', 'iran', 'iraq',
      'ireland', 'israel', 'italy', 'jamaica', 'japan', 'jordan', 'kazakhstan', 'kenya', 'kiribati', 'kosovo', 'kuwait',
      'kyrgyzstan', 'laos', 'latvia', 'lebanon', 'lesotho', 'liberia', 'libya', 'liechtenstein', 'lithuania',
      'luxembourg', 'macedonia', 'madagascar', 'malawi', 'malaysia', 'maldives', 'mali', 'malta', 'marshall',
      'mauritania', 'mauritius', 'mexico', 'micronesia', 'moldova', 'monaco', 'mongolia', 'montenegro', 'morocco',
      'mozambique', 'myanmar', 'namibia', 'nauru', 'nepal', 'netherlands', 'new_zealand', 'nicaragua', 'niger',
      'nigeria', 'north_korea', 'norway', 'oman', 'pakistan', 'palau', 'palestine', 'panama', 'papua',
      'paraguay', 'peru', 'philippines', 'poland', 'portugal', 'qatar', 'romania', 'russia', 'rwanda',
      'st_kitts', 'saint_lucia', 'st_vincent', 'samoa', 'san_marino', 'sao_tome', 'saudi_arabia',
      'senegal', 'serbia', 'seychelles', 'sierra_leone', 'singapore', 'slovakia', 'slovenia', 'solomon',
      'somalia', 'south_africa', 'south_korea', 'south_sudan', 'spain', 'sri_lanka', 'sudan', 'suriname', 'swaziland',
      'sweden', 'switzerland', 'syria', 'taiwan', 'tajikistan', 'tanzania', 'thailand', 'timor-leste', 'togo', 'tonga',
      'trinidad', 'tunisia', 'turkey', 'turkmenistan', 'tuvalu', 'uganda', 'ukraine', 'emirates', 'united_kingdom',
      'america', 'uruguay', 'uzbekistan', 'vanuatu', 'vatican', 'venezuela', 'vietnam', 'yemen', 'zambia', 'zimbabwe']
