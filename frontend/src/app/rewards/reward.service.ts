import { Injectable } from '@angular/core';
import { AngularFirestore } from '@angular/fire/firestore';
import { TweetData } from './twitterdata'
import { PowTweetInfo } from './pow_tweet_info'
import { map } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class RewardService {

  constructor(private firestore: AngularFirestore,private http: HttpClient) { }

  getRewardsDetails(tweetId: string): Observable<TweetData[]> { 
    const data$ = this.firestore.collection("tweetData", ref => ref.where('tweet_id', '==', tweetId));
    return data$.snapshotChanges()
    .pipe(map(snaps =>  {
      return snaps.map(snap => {
        return <TweetData>  {
          id:snap.payload.doc.id,
          ...snap.payload.doc.data() as TweetData
        };
      });
    }));
 }

  getTweetDate(tweetId) : Observable<any> 
  {
    const data$ = this.firestore.collection("pow_tweet_info", ref => ref.where('tweet_id', '==', tweetId));
    return data$.snapshotChanges()
    .pipe(map(snaps =>  {
      return snaps.map(snap => {
        return <PowTweetInfo>  {
          id:snap.payload.doc.id,
          ...snap.payload.doc.data() as PowTweetInfo
        };
      });
    }));
  }

}
