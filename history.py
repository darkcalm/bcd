from agents import Diagram, DiagramAgent
from actions import DiagramAction

places = {}
places["955e7e81b6120cad67ce9890b9d18276"] = Diagram(name="twobytwo", meta={'scale': 1}, agents=[
    DiagramAgent(key='q1', info="quadrant 1", actions=[
        DiagramAction(at='cartesian(4,4) (1,1)'),
        DiagramAction(plan='text'),
        DiagramAction(draw='text')
    ]),
    DiagramAgent(key='q2', info="quadrant 2", actions=[
        DiagramAction(at='cartesian(4,4) (-1,1)'),
        DiagramAction(plan='text'),
        DiagramAction(draw='text')
    ]),
    DiagramAgent(key='q3', info="quadrant 3", actions=[
        DiagramAction(at='cartesian(4,4) (-1,-1)'),
        DiagramAction(plan='text'),
        DiagramAction(draw='text')
    ]),
    DiagramAgent(key='q4', info="quadrant 4", actions=[
        DiagramAction(at='cartesian(4,4) (1,-1)'),
        DiagramAction(plan='text'),
        DiagramAction(draw='text')
    ]),
    DiagramAgent(key='xp', info="positive x", actions=[
        DiagramAction(at='cartesian(4,4) (2,0)'),
        DiagramAction(plan='text, line(x)'),
        DiagramAction(draw='text')
    ]),
    DiagramAgent(key='xn', info="negative x", actions=[
        DiagramAction(at='cartesian(4,4) (-2,0)'),
        DiagramAction(plan='text, line(x)'),
        DiagramAction(draw='text')
    ]),
    DiagramAgent(key='yp', info="positive y", actions=[
        DiagramAction(at='cartesian(4,4) (0,2)'),
        DiagramAction(plan='text, line(y)'),
        DiagramAction(draw='text')
    ]),
    DiagramAgent(key='yn', info="negative y", actions=[
        DiagramAction(at='cartesian(4,4) (0,-2)'),
        DiagramAction(plan='text, line(y)'),
        DiagramAction(draw='text')
    ]),
    DiagramAgent(key='x', info="axis x", actions=[
        DiagramAction(at='cartesian(4,4) (1,0)'),
        DiagramAction(plan='text'),
        DiagramAction(draw='line, text')
    ]),
    DiagramAgent(key='y', info="axis y", actions=[
        DiagramAction(at='cartesian(4,4) (0,1)'),
        DiagramAction(plan='text'),
        DiagramAction(draw='line, text')
    ]),
    DiagramAgent(key='t', info="title", actions=[
        DiagramAction(at='cartesian(4,4) (-2,2)'),
        DiagramAction(plan='text'),
            DiagramAction(draw='text')
    ])
])

places["2d203aaff5b2a70c5a24fab8c26a0095"] = Diagram(name="twoofthree", meta={'scale': 1}, agents=[
    DiagramAgent(key='u', info="top corner", actions=[
        DiagramAction(at='polar(6,2) (0,1)'),
        DiagramAction(plan='text, line(-l), line(-r)'),
        DiagramAction(draw=['text'])
    ]),
    DiagramAgent(key='l', info="left corner", actions=[
        DiagramAction(at='polar(6,2) (2,1)'),
        DiagramAction(plan='text, line(-r), line(-u)'),
        DiagramAction(draw='text')
    ]),
    DiagramAgent(key='r', info="right corner", actions=[
        DiagramAction(at='polar(6,2) (4,1)'),
        DiagramAction(plan='text, line(-u), line(-l)'),
        DiagramAction(draw='text')
    ]),
    DiagramAgent(key='-u/lr/rl', info="bottom side", actions=[
        DiagramAction(at='middle(l,r)'),
        DiagramAction(plan='text'),
        DiagramAction(draw='line, text')
    ]),
    DiagramAgent(key='-l/ur/ru', info="right side", actions=[
        DiagramAction(at='middle(u,r)'),
        DiagramAction(plan='text'),
        DiagramAction(draw='line, text')
    ]),
    DiagramAgent(key='-r/ul/lu', info="left side", actions=[
        DiagramAction(at='middle(u,l)'),
        DiagramAction(plan='text'),
        DiagramAction(draw='line, text')
    ]),
    DiagramAgent(key='t', info="title", actions=[
        DiagramAction(at='cartesian(2,2) (-1,1)'),
        DiagramAction(plan='text'),
        DiagramAction(draw='text')
    ])
])