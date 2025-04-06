""""""
from flask import request, jsonify

from lib.edu.blooms import lo_chat

fmt1 = ['Knowledge', 'Comprehension', 'Application', 'Analysis', 'Synthesis', 'Evaluation']
fmt2 = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']

mapping_fmt2_to_fmt1 = {
    'Remember': 'Knowledge',
    'Understand': 'Comprehension',
    'Apply': 'Application',
    'Analyze': 'Analysis',
    'Evaluate': 'Evaluation',
    'Create': 'Synthesis'
}

def lo_route():
    stage = request.args.get('stage', None)
    topic = request.args.get('topic', None)

    if not stage or not topic:
        return jsonify({"error": "Invalid request."}), 400

    if stage.lower() not in [stg.lower() for stg in fmt1 + fmt2]:
        return jsonify({"error": "Invalid stage."}), 400

    if stage in fmt2:
        stage = mapping_fmt2_to_fmt1[stage]

    response = lo_chat(stage, topic)

    return jsonify(dict(objective=response))
