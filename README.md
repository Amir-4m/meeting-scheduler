# meeting-scheduler

This project provides Django APIs (graphQL) for clients.

users can create  a schedule of available dates and times and select their desired meeting intervals (15 min / 30 min / 45 min) and
other users can reserve the meeting schedule.

# How to run the project
- Ensure that you've installed python>=3.7 and pip3 latest version.
- Create a database for the project. (default DB engine for project is postgresql, but you can change it in the settings.)
    
    `CREATE DATABASE db_name`

- You can create venv for the project using `python -m venv <project_dir>`
- Install requirements using `pip install -r requirements`
- Create a `.env` file in the project root and fill it using `sample.env` file.
- Run `python manage.py migrate` command.
- You can create a super user for accessing the admin panel using `python manage.py createsuperuser`.
- Run server using `python manage.py runserver 127.0.0.1:8000`


# GraphQL schema and queries
let's see a list of available queries and mutations.

graph URL: http://127.0.0.1:8000/graphql

### Create meetings
```gql
mutation meetingMutation {
  createUpdateMeeting(input: {
    title: "meeting title", 
    description: "meeting description",
    interval:"30",
    schedules:[
      {
        availableAt:"2022-01-23T15:59:15+00:00"
      },
      {
        availableAt:"2022-02-13T15:59:15+00:00"
      }
    ]
    
  }) {
    id
    title
    description
    errors {
      field
      messages
    }
  }
}
```
### Update meetings
```gql
mutation meetingMutation {
  createUpdateMeeting(input: {
    id:1
    title: "updated meeting title", 
    
  }) {
    id
    title
    description
    errors {
      field
      messages
    }
  }
}
```
### Delete meetings
```gql
mutation deleteMutation {
  deleteMeeting(id: 1) {
    deleted
  }
}
```

### Delete meeting schedule
```gql
mutation deleteMutation {
  deleteMeetingSchedule(id: 5) {
    deleted
  }
}
```

### Read user meetings (login required)
```gql
uery userQuery{
  myMeetings{
    edges{
      node{
        id
        objectId
        title
        description
        interval
        schedules{
          edges{
            node{
              isActive
              availableAt
              isReserved
              objectId
            }
          }
        }
      }
    }
  }
}
```

### Read all meetings with their schedules
```gql
query Query {
  meetings {
    edges {
      node {
        id
        objectId
        user {
          id
          objectId
          email
          username
        }
        schedules {
          edges {
            node {
              id
              availableAt
              isReserved
            }
          }
        }
      }
    }
  }
}
```
### Read all meetings and timings for a specific user
```gql
query Query {
  meetings(user: "<user_global_id>") {
    edges {
      node {
        id
        objectId
        user {
          id
          objectId
          email
          username
        }
        schedules {
          edges {
            node {
              id
              availableAt
              isReserved
            }
          }
        }
      }
    }
  }
}
```

### Read all available timings for a specific user
```gql
query Query{
  meetingSchedules(meeting:"<meeting_global_id>", isReserved:false){
    edges{
      node{
        id
        availableAt
        meeting{
          id
          objectId
          title
          description
        }
        isReserved
        objectId
      }
    }
  }
}
```

### Create a reservation for specific meeting
```gql
mutation meetingRMutation {
  createReservedMeeting(input: {
    guestEmail:"guestemail@domain.com"
    guestFullname:"guest fullname"
    meetingSchedule:"<meeting_schedule_pk>"
    
  }) {
    id
    errors {
      field
      messages
    }
  }
}

```
