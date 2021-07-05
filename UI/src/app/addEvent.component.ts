import { formatDate } from "@angular/common";
import { Component } from "@angular/core";
import { FormBuilder, Validators } from "@angular/forms";
import { WebService } from "./web.service";


@Component({
    selector: 'addEvent',
    templateUrl: './addEvent.component.html',
    styleUrls: ['./addEvent.component.css']
})

export class addEventComponent {
    constructor(private webService: WebService,
        private formBuilder: FormBuilder) {}

    eventForm;
    selectedTrack;
    trackID;
    tracksList: Array<Object> = []
    
    ngOnInit(){
        this.getForm()
    }

    getForm(){
        this.webService.getAllTracks().subscribe((data) => 
        { for(var entry = 0; entry < data.length; entry++){ 
            this.tracksList.push(data[entry]); 
        }})
        
        this.eventForm = this.formBuilder.group({
        trackName:['', Validators.required],
        event: ['', Validators.required],
        series: ['', Validators.required],
        date: [formatDate(Date.now(), 'yyyy-MM-dd', 'en'), Validators.required],
        time: ['00:00',Validators.required],
        notes: ['N/A', Validators.required] 
        }); 
    }
    trackSelected(){
        this.trackID = this.selectedTrack._id
    }
    
    onSubmit(){
        this.webService.postEvent(this.eventForm.value, this.trackID)
        this.eventForm.reset()
        this.ngOnInit();
    }

    isInvalid(control) {
        return this.eventForm.controls[control].invalid &&
               this.eventForm.controls[control].touched;
        }
        
    isUnTouched() {
        return this.eventForm.controls.trackName.pristine ||
                this.eventForm.controls.event.pristine ||
               this.eventForm.controls.series.pristine;
    }

    isIncomplete() {
            return this.isInvalid('event') ||
            this.isInvalid('series') ||
            this.isInvalid('date') ||
            this.isInvalid('time') ||
            this.isInvalid('notes') ||
            this.isUnTouched();
    }
    
}


    