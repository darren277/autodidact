""""""
from settings import OPENPROJECT_URL, OPENPROJECT_API_KEY
from pyopenproject.openproject import OpenProject
import pyopenproject

op = OpenProject(url=OPENPROJECT_URL, api_key=OPENPROJECT_API_KEY)

# TODO: Save the actual Work Package attachment binaries (into project specific folder)...


def serialize_work_package(wp: pyopenproject.model.work_package.WorkPackage):
    d = dict()
    try:
        d.update(wp.__dict__)
        del d['_links']

        # Skipping cost related attributes.
        del d['laborCosts']
        del d['materialCosts']
        del d['overallCosts']

        type_link = wp._links.get('type', None)
        type_title = type_link.get('title', None)

        d.update(type=type_title)

        if type_title == 'Module':
            lessons = wp._links.get('children')
            '''
            # Example of lessons:
                [
                    {'href': '/api/v3/work_packages/46', 'title': 'Lesson 1.2: History and Development of Anthropology'},
                    {'href': '/api/v3/work_packages/47', 'title': 'Lesson 1.3: Research Methods in Anthropology'},
                    {'href': '/api/v3/work_packages/45', 'title': 'Lesson 1.1: What is Anthropology?'},
                    {'href': '/api/v3/work_packages/54', 'title': 'Module 1 Exam'}
                ]
            '''
            if not lessons:
                raise Exception("No lessons found in module.")
            d.update(lessons=lessons)
        elif type_link == 'Lesson':
            # Just in case we need special logic for lessons (like for attachments, etc).
            ...
        elif type_link == 'Exam':
            # Just in case we need special logic for exams.
            ...

        # Currently unavailable attributes: Custom fields, attachments, activities, and revisions.

        # TODO: Attachments.
        #attachments_link = d['_links'].get('attachments', None)
        # try:
        #     d.update(attachments=extract_work_package_attachments(wp))
        # except Exception as e:
        #     print(f"Failed to serialize work package attachments. {e}")

        # TODO: Relations (more fundamental for our use case at the moment).
        # Will be for structured both module and lesson order.

        #wp_service = op.get_work_package_service()
        #relations = wp_service.find_relations(wp)
        #print(relations)
    except Exception as e:
        print(f"Failed to serialize work package. {e}")
        breakpoint()
    return d



def extract_project_work_packages(project: pyopenproject.model.project.Project):
    try:
        work_packages = op.get_project_service().find_work_packages(project)
    except Exception as e:
        print(f"Failed to extract project work packages for Project ({project.identifier}). {e}")
        return

    return [serialize_work_package(wp) for wp in work_packages]


def serialize_project(project: pyopenproject.model.project.Project):
    # Currently does not handle custom fields.

    try:
        work_packages = extract_project_work_packages(project)
    except Exception as e:
        print(f"Failed to extract project ({project.identifier}) work packages. {e}")
        return

    modules = []

    for wp in work_packages:
        module = dict(
            lessons=[]
        )
        if wp['type'] == 'Module':
            for lesson in wp['lessons']:
                _id = lesson['href'].split('/')[-1]
                current_wp = [w for w in work_packages if int(w['id']) == int(_id)][0]
                if current_wp['type'] == 'Lesson':
                    module['lessons'].append(current_wp)
                elif current_wp['type'] == 'Exam':
                    module['exam'] = current_wp
            module.update(
                id=wp['id'],
                title=wp['subject'],
                description=wp['description'],
                createdAt=wp['createdAt'],
                updatedAt=wp['updatedAt']
            )
            modules.append(module)

    course = dict(
        id=project.id,
        identifier=project.identifier,
        name=project.name,
        description=project.description,
        modules=modules
    )

    return course


def export_project(course_name: str = None):
    try:
        project = [p for p in op.get_project_service().find_all() if p.identifier == course_name][0]
    except Exception as e:
        print(f"Failed to export project. {e}")
        return

    data = serialize_project(project)

    print(f'Course name: {data["name"]}')
    print(f'Course ID: {data["id"]}')
    print(f'Course description: {data["description"]}')
    print(f'Course modules: {data["modules"]}')
    print(f'Course modules count: {len(data["modules"])}')

    return data
