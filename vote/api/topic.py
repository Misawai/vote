from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Annotated
from datetime import datetime
from vote.domain.topic import (
    TopicService,
    UpdateTopicInput,
    Topic,
    Option,
    TopicStage,
    CreateTopicInput,
)
from . import get_topic_service

router = APIRouter()


class TopicResponse(BaseModel):

    class Config:
        orm_mode = True

    id: str
    description: str
    starts_at: datetime
    ends_at: datetime
    created_at: datetime
    updated_at: datetime
    options: list[Option]
    stage: TopicStage

    @classmethod
    def from_topic(cls, topic: Topic):
        return cls.from_orm(topic)


class TopicDetailResponse(BaseModel):

    class Config:
        orm_mode = True

    id: str
    description: str
    starts_at: datetime
    ends_at: datetime
    created_at: datetime
    updated_at: datetime
    options: list[Option]
    stage: TopicStage

    @classmethod
    def from_topic(cls, topic: Topic):
        return cls.from_orm(topic)


class CreateTopicResponse(BaseModel):
    id: str


topic_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Topic not found',
)


@router.get('/', response_model=list[TopicResponse])
async def get_all_topic(svc: Annotated[
    TopicService,
    Depends(get_topic_service),
]):
    '''
    Get all topics.
    '''
    topics = await svc.get_all()
    return [TopicResponse.from_topic(t) for t in topics]


@router.get('/{topic_id}', response_model=TopicDetailResponse)
async def get_one_topic(
    topic_id: str,
    svc: Annotated[
        TopicService,
        Depends(get_topic_service),
    ],
):
    '''
    Get single topic by id.
    '''
    topic = await svc.get_by_id(topic_id)
    if topic is None:
        raise topic_not_found_exception
    return TopicDetailResponse.from_topic(topic)


@router.post('/', response_model=CreateTopicResponse)
async def create_topic(
    input: CreateTopicInput,
    svc: Annotated[
        TopicService,
        Depends(get_topic_service),
    ],
):
    '''
    Create new topic.
    '''
    id = await svc.new(input)
    return CreateTopicResponse(id=id)


@router.patch('/{topic_id}')
async def update_topic(
    topic_id: str,
    svc: Annotated[
        TopicService,
        Depends(get_topic_service),
    ],
    input: UpdateTopicInput,
):
    '''
    Update single topic. Only allowed before vote started.
    '''
    topic = await svc.get_by_id(topic_id)
    if topic is None:
        raise topic_not_found_exception
    topic.update(input)
    await svc.save(topic)


@router.get('/{topic_id}/vote-result')
async def get_vote_result(topic_id: str):
    '''
    Get vote result of a topic.
    '''
