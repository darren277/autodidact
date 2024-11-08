""""""

def serialize(event):
    return dict(
        event=event.event,
        data=dict(
            delta=dict(
                content=[
                    dict(
                        text=dict(
                            value=event.data.delta.content[i].text.value
                        )
                    ) for i in range(len(event.data.delta.content))
                ]
            )
        )
    )
