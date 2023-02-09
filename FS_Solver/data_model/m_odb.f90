! Description:
! Definition of an output database.
module m_odb
    implicit none
    
    private
    public t_odb, new_odb
    
    type t_odb
        integer                    :: n_frames       ! number of frames (increments or modes)
        integer                    :: n_nsfields     ! number of nodal scalar fields
        character(64), allocatable :: frame_descr(:) ! frame descriptions
        character(64), allocatable :: specs(:)       ! specifications of the nodal scalar fields
        real,          allocatable :: values(:, :)   ! values of the nodal scalar fields
    contains
        procedure :: set_frame_descr, set_nsfield
        final     :: destructor
    end type
    
    interface new_odb
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Output database constructor.
    type(t_odb) function constructor(n_nodes, n_frames, n_nsfields) result(this)
        integer, intent(in) :: n_nodes    ! number of mesh nodes
        integer, intent(in) :: n_frames   ! number of frames (increments or modes)
        integer, intent(in) :: n_nsfields ! number of nodal scalar fields
        this%n_frames   = n_frames
        this%n_nsfields = n_nsfields
        allocate(this%frame_descr(this%n_frames))
        allocate(this%specs(this%n_nsfields))
        allocate(this%values(n_nodes, this%n_nsfields))
    end function
    
    ! Description:
    ! Output database destructor.
    subroutine destructor(this)
        type(t_odb), intent(inout) :: this
        if (allocated(this%frame_descr)) deallocate(this%frame_descr)
        if (allocated(this%specs))       deallocate(this%specs)
        if (allocated(this%values))      deallocate(this%values)
    end subroutine
    
    ! Description:
    ! Sets the frame description.
    subroutine set_frame_descr(this, index, description)
        class(t_odb), intent(inout) :: this
        character(*), intent(in)    :: description
        integer,      intent(in)    :: index
        this%frame_descr(index) = description
    end subroutine
    
    ! Description:
    ! Sets the nodal scalar field data.
    subroutine set_nsfield(this, index, spec, values)
        class(t_odb), intent(inout) :: this
        character(*), intent(in)    :: spec
        integer,      intent(in)    :: index
        real,         intent(in)    :: values(:)
        this%specs(index)     = spec
        this%values(:, index) = values
    end subroutine
    
end module
