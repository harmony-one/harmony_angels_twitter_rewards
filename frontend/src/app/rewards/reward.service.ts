import { Injectable } from '@angular/core';
import { AngularFirestore } from '@angular/fire/firestore';
import { TweetData } from './twitterdata'
import { map } from 'rxjs/operators';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class RewardService {

  constructor(private firestore: AngularFirestore ) { }

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
}
